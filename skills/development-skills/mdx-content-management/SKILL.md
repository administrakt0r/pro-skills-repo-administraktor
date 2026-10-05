---
name: mdx-content-management
description: >-
  Manage, validate, compile, and render MDX (Markdown + JSX) content in modern web
  applications. Use when building content pipelines, technical documentation, blogs,
  component mappings, syntax highlighting, Zod frontmatter validation, or RSS feeds.
---

# MDX Content Management

MDX blends standard Markdown formatting with executable React/JSX components, allowing technical authors and developers to embed rich, interactive widgets alongside static prose. Effective MDX management requires a robust build pipeline: validating YAML frontmatter against strict schemas, transforming Abstract Syntax Trees (ASTs) via Remark and Rehype plugins, mapping standard HTML tags to accessible React primitives, and generating static metadata for SEO and syndication feeds.

For complete implementation blueprints, configuration files, and ready-to-use component maps, consult the companion guide in [references/content-patterns.md](references/content-patterns.md).

---

## When to Use

- Developing documentation portals, engineering blogs, marketing landing hubs, or changelogs using React or Next.js.
- Embedding interactive components (tabs, callouts, copy-ready code blocks, sandboxes) within technical Markdown articles.
- Enforcing type safety and validation rules across content metadata (authors, publish dates, tags, slugs) at build time.
- Migrating from legacy Markdown parsers to modern AST-driven compilation pipelines.
- Implementing code block syntax highlighting (Shiki, Prism), table of contents generators, and autolinked headings.
- Generating automated syndication feeds (RSS 2.0 / Atom) and dynamic OpenGraph / SEO tags directly from content collections.

---

## Prerequisites

- **Node.js**: Version 18.18+ or 20+ (LTS recommended).
- **Core Runtime**: React 18 or React 19.
- **Framework Support**: Next.js App Router or modern React static site generator.
- **Key Dependencies**:
  ```bash
  # Core validation & frontmatter parsing
  npm install zod gray-matter reading-time

  # Content compilation (choose your engine: next-mdx-remote, velite, or @next/mdx)
  npm install next-mdx-remote

  # Remark & Rehype AST plugin ecosystem
  npm install remark-gfm rehype-slug rehype-autolink-headings rehype-pretty-code shiki
  ```

---

## Steps

### 1. Define Type-Safe Frontmatter Schemas with Zod

Treat content files with the same strictness as database records. Define a Zod schema to enforce types, handle defaults, and catch missing frontmatter fields during the build rather than at runtime.

```typescript
// lib/content-schema.ts
import { z } from "zod";

export const AuthorSchema = z.object({
  name: z.string().min(1, "Author name is required"),
  role: z.string().default("Contributor"),
  avatar: z.string().url().or(z.string().startsWith("/")),
  twitter: z.string().optional(),
});

export const PostFrontmatterSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters").max(100),
  description: z.string().min(10).max(250),
  publishedAt: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Format must be YYYY-MM-DD"),
  updatedAt: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  coverImage: z.string().optional(),
  coverImageAlt: z.string().optional(),
  category: z.string().default("Engineering"),
  tags: z.array(z.string()).default([]),
  draft: z.boolean().default(false),
  featured: z.boolean().default(false),
  author: AuthorSchema,
});

export type PostFrontmatter = z.infer<typeof PostFrontmatterSchema>;
```

### 2. Choose and Configure the Content Engine Pipeline

Select the content pipeline architecture that matches your performance and workflow goals:

| Engine | Best For | Architecture | Highlights |
| :--- | :--- | :--- | :--- |
| **`next-mdx-remote/rsc`** | Next.js App Router | Zero client runtime (RSC) | Dynamic or static parsing; full control over filesystem and plugins. |
| **Velite** | Large static collections | Build-time compilation | Fast, generates TypeScript types and `.json` cache directly from schemas. |
| **`@next/mdx`** | Route-level pages | Webpack/Turbopack plugin | Native imports (`import Post from './post.mdx'`); minimal overhead. |
| **Contentlayer (Legacy)** | Legacy codebases | Unmaintained / Forked | Requires community patches for modern Next.js/React versions. |

#### Option A: RSC Engine with `next-mdx-remote` (Recommended for Next.js App Router)

Create a filesystem loader with caching and frontmatter validation:

```typescript
// lib/content.ts
import fs from "node:fs/promises";
import path from "node:path";
import matter from "gray-matter";
import readingTime from "reading-time";
import { PostFrontmatterSchema, PostFrontmatter } from "./content-schema";

const POSTS_DIR = path.join(process.cwd(), "content/posts");

export interface Post {
  slug: string;
  frontmatter: PostFrontmatter;
  content: string;
  readingMinutes: number;
}

export async function getPost(slug: string): Promise<Post | null> {
  const filePath = path.join(POSTS_DIR, `${slug}.mdx`);
  try {
    const raw = await fs.readFile(filePath, "utf-8");
    const { data, content } = matter(raw);
    const frontmatter = PostFrontmatterSchema.parse(data);
    const stats = readingTime(content);

    return {
      slug,
      frontmatter,
      content,
      readingMinutes: Math.ceil(stats.minutes),
    };
  } catch (error) {
    return null;
  }
}
```

#### Option B: Velite Build-Time Engine

Configure `velite.config.ts` for automated TypeScript generation:

```typescript
// velite.config.ts
import { defineConfig, defineCollection, s } from "velite";

const posts = defineCollection({
  name: "Post",
  pattern: "posts/**/*.mdx",
  schema: s.object({
    title: s.string().max(100),
    description: s.string().max(250),
    publishedAt: s.isodate(),
    slug: s.path(),
    draft: s.boolean().default(false),
    tags: s.array(s.string()).default([]),
    body: s.mdx(),
  }),
});

export default defineConfig({
  root: "content",
  output: { data: ".velite", clean: true },
  collections: { posts },
});
```

### 3. Configure Remark and Rehype Plugins

The MDX compilation process operates in two stages:
1. **Remark (Markdown AST - mdast)**: Operates on Markdown syntax (e.g., GitHub Flavored Markdown tables, task lists, footnotes via `remark-gfm`).
2. **Rehype (HTML AST - hast)**: Operates on HTML elements (e.g., heading slugification via `rehype-slug`, linking via `rehype-autolink-headings`, syntax highlighting via `rehype-pretty-code`).

Assemble the shared plugin array:

```typescript
// lib/mdx-plugins.ts
import remarkGfm from "remark-gfm";
import rehypeSlug from "rehype-slug";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypePrettyCode, { type Options as PrettyCodeOptions } from "rehype-pretty-code";

const prettyCodeOptions: PrettyCodeOptions = {
  theme: "github-dark",
  keepBackground: false,
  onVisitLine(node) {
    // Prevent empty lines from collapsing
    if (node.children.length === 0) {
      node.children = [{ type: "text", value: " " }];
    }
  },
  onVisitHighlightedLine(node) {
    node.properties.className = (node.properties.className || []).concat("line--highlighted");
  },
  onVisitHighlightedWord(node) {
    node.properties.className = ["word--highlighted"];
  },
};

export const mdxOptions = {
  remarkPlugins: [remarkGfm],
  rehypePlugins: [
    rehypeSlug,
    [rehypePrettyCode, prettyCodeOptions],
    [
      rehypeAutolinkHeadings,
      {
        behavior: "wrap",
        properties: {
          className: ["heading-anchor"],
          ariaLabel: "Link to section",
        },
      },
    ],
  ],
};
```

### 4. Implement Code Block Syntax Highlighting (Shiki vs. Prism)

- **Shiki (`rehype-pretty-code`)**: Performs syntax highlighting at build time using VS Code TextMate grammars. Generates pre-colored HTML spans without client JavaScript. Highly recommended.
- **Prism**: Runtime or build-time regex tokenizer. Lighter HTML output, but less accurate and requires client themes.

Add the following CSS rules to your global stylesheet (`globals.css`) for Shiki highlighting:

```css
/* Shiki & rehype-pretty-code styles */
code[data-theme*=" "],
code[data-theme*=" "] span {
  color: var(--shiki-light);
  background-color: var(--shiki-light-bg);
}

@media (prefers-color-scheme: dark) {
  code[data-theme*=" "],
  code[data-theme*=" "] span {
    color: var(--shiki-dark);
    background-color: var(--shiki-dark-bg);
  }
}

.line--highlighted {
  background-color: rgba(255, 255, 255, 0.1);
  border-left: 2px solid #3b82f6;
  padding-left: 0.5rem;
}

.word--highlighted {
  background-color: rgba(255, 255, 255, 0.15);
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
}

[data-rehype-pretty-code-title] {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-family: monospace;
  background: #18181b;
  border: 1px solid #27272a;
  border-bottom: none;
  border-top-left-radius: 0.5rem;
  border-top-right-radius: 0.5rem;
  color: #a1a1aa;
}
```

### 5. Define Custom MDX Component Mappings & Dynamic Imports

Map standard HTML elements and custom JSX elements into the MDX compilation scope:

```tsx
// components/mdx/components.tsx
import React, { ComponentPropsWithoutRef } from "react";
import Image, { ImageProps } from "next/image";
import Link from "next/link";
import dynamic from "next/dynamic";

// Dynamic import for heavy or interactive client-only widgets
const LiveEditor = dynamic(() => import("@/components/interactive/live-editor"), {
  loading: () => <div className="h-48 rounded bg-neutral-900 animate-pulse" />,
  ssr: false,
});

export const customMdxComponents = {
  // Override native heading elements
  h2: ({ id, children, ...props }: ComponentPropsWithoutRef<"h2">) => (
    <h2 id={id} className="text-2xl font-bold mt-8 mb-4 tracking-tight scroll-m-20" {...props}>
      {children}
    </h2>
  ),

  // Smart Link handling: internal Next.js links vs external target="_blank"
  a: ({ href = "", children, ...props }: ComponentPropsWithoutRef<"a">) => {
    if (href.startsWith("/") || href.startsWith("#")) {
      return (
        <Link href={href} className="text-blue-500 hover:underline" {...props}>
          {children}
        </Link>
      );
    }
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline" {...props}>
        {children}
      </a>
    );
  },

  // Optimized Next.js image replacement
  img: (props: any) => (
    <figure className="my-6">
      <Image
        src={props.src}
        alt={props.alt || ""}
        width={1200}
        height={675}
        className="rounded-lg border border-neutral-800"
        sizes="(max-width: 768px) 100vw, 800px"
      />
      {props.alt && (
        <figcaption className="text-center text-xs text-neutral-400 mt-2">
          {props.alt}
        </figcaption>
      )}
    </figure>
  ),

  // Custom Admonition/Callout
  Callout: ({ type = "info", children }: { type?: "info" | "warning" | "danger"; children: React.ReactNode }) => {
    const borders = {
      info: "border-blue-500 bg-blue-500/10 text-blue-200",
      warning: "border-amber-500 bg-amber-500/10 text-amber-200",
      danger: "border-red-500 bg-red-500/10 text-red-200",
    }[type];
    return <aside className={`p-4 my-6 rounded border-l-4 ${borders}`}>{children}</aside>;
  },

  // Dynamic interactive widget
  LiveEditor,
};
```

### 6. Construct Blog Site Architecture & Dynamic Routing

Implement the dynamic route using Next.js App Router conventions:

```tsx
// app/blog/[slug]/page.tsx
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { MDXRemote } from "next-mdx-remote/rsc";

import { getPost, getAllPosts } from "@/lib/content";
import { mdxOptions } from "@/lib/mdx-plugins";
import { customMdxComponents } from "@/components/mdx/components";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const posts = await getAllPosts();
  return posts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug);
  if (!post) return { title: "Post Not Found" };

  const { title, description, publishedAt, coverImage, tags } = post.frontmatter;
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";

  return {
    title,
    description,
    keywords: tags,
    openGraph: {
      title,
      description,
      type: "article",
      publishedTime: publishedAt,
      url: `${siteUrl}/blog/${slug}`,
      images: coverImage ? [{ url: `${siteUrl}${coverImage}` }] : undefined,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
  };
}

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = await getPost(slug);

  if (!post) notFound();

  return (
    <article className="max-w-3xl mx-auto py-12 px-4">
      <header className="mb-8">
        <h1 className="text-4xl font-extrabold mb-3">{post.frontmatter.title}</h1>
        <p className="text-neutral-400 text-sm">
          Published {post.frontmatter.publishedAt} &bull; {post.readingMinutes} min read
        </p>
      </header>

      <div className="prose prose-invert max-w-none">
        <MDXRemote
          source={post.content}
          components={customMdxComponents}
          options={{ mdxOptions }}
        />
      </div>
    </article>
  );
}
```

### 7. Generate RSS Feeds from MDX Content

Automate XML syndication for content readers and aggregators using a Route Handler:

```typescript
// app/rss.xml/route.ts
import { getAllPosts } from "@/lib/content";

export async function GET() {
  const posts = await getAllPosts();
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";

  const itemsXml = posts
    .map(
      (post) => `
    <item>
      <title><![CDATA[${post.frontmatter.title}]]></title>
      <link>${siteUrl}/blog/${post.slug}</link>
      <guid>${siteUrl}/blog/${post.slug}</guid>
      <description><![CDATA[${post.frontmatter.description}]]></description>
      <pubDate>${new Date(post.frontmatter.publishedAt).toUTCString()}</pubDate>
    </item>`
    )
    .join("");

  const rss = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Engineering Blog</title>
    <link>${siteUrl}/blog</link>
    <description>Latest technical insights and architecture notes.</description>
    <language>en-US</language>
    <atom:link href="${siteUrl}/rss.xml" rel="self" type="application/rss+xml"/>
    ${itemsXml}
  </channel>
</rss>`;

  return new Response(rss.trim(), {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "s-maxage=3600, stale-while-revalidate",
    },
  });
}
```

---

## Best Practices

- **Validate at Build Time**: Use Zod or Velite schemas to fail early when required frontmatter attributes (title, date, author) are missing or misformatted.
- **RSC by Default**: Keep MDX parsing on React Server Components (`next-mdx-remote/rsc`). Never send parsing libraries or full Remark/Rehype pipelines to the client browser bundle.
- **Isolate Client Interactivity**: When embedding interactive React widgets into MDX, declare `"use client"` only on that specific leaf widget, not on the entire MDX renderer or article layout.
- **Use `next/dynamic` for Heavy Widgets**: Dynamically import complex interactive components (such as code sandboxes, charting libraries, or 3D models) so readers only load JS bundles for articles that contain them.
- **Sanitize Untrusted Content**: If MDX input originates from external CMS editors or user contributions, pass content through `rehype-sanitize` with a strict schema to prevent XSS.
- **Responsive Media**: Always map `img` or `<Image />` to modern components specifying aspect ratio, responsive `sizes`, and WebP/AVIF formatting to avoid layout shift (CLS).
- **Structure Content Hierarchies**: Maintain clear directory separation (e.g., `content/posts/`, `content/docs/`, `content/changelog/`) with distinct Zod schemas per collection.

---

## Common Pitfalls

- **ESM vs. CommonJS Plugin Incompatibilities**: Most Remark/Rehype plugins (e.g., `remark-gfm`, `rehype-slug`) are pure ESM. Ensure your configuration file (`next.config.mjs`, `velite.config.ts`) uses ESM syntax and module extensions.
- **Missing Frontmatter Separation**: Failing to slice off YAML frontmatter before passing raw text to the MDX compiler can trigger compile-time syntax errors or unwanted frontmatter text rendering in the document body. Always use `gray-matter` or a content layer.
- **Passing Unsupported Data Types to Server/Client Boundaries**: Passing complex functions or non-serializable objects as props into MDX components will trigger Next.js serialization warnings.
- **Cumulative Layout Shift (CLS) on Images**: Rendering MDX images without explicit `width`/`height` or without `aspect-ratio` containers causes page content to jump as assets download.
- **Unescaped Curly Brackets or HTML Entities**: In MDX, raw `{` and `<` characters are evaluated as JSX expressions. Authors must escape them (`\{` or `&lt;`) or wrap them in backticks (`\`{code}\``).

---

## Verification

To confirm the MDX system functions properly, execute these verification checks:

1. **Schema & Type Validation**:
   ```bash
   npx tsc --noEmit
   ```
   Ensures all frontmatter interfaces, component mappings, and loaders satisfy TypeScript types.

2. **Build and Static Generation**:
   ```bash
   npm run build
   # or
   pnpm build
   ```
   Confirms `generateStaticParams()` successfully compiles all MDX routes and frontmatter validation passes with zero errors.

3. **AST Transformation & Anchors**:
   - Inspect a rendered article in the browser.
   - Confirm headings contain auto-generated IDs (`id="heading-name"`) and clickable anchor links.
   - Confirm code blocks display syntax highlighting colors from Shiki without client flash.

4. **Syndication & SEO Inspection**:
   - Navigate to `/rss.xml` and verify the XML document is well-formed using an XML validator or feed reader.
   - Inspect `<head>` tags on article pages to verify OpenGraph metadata (`og:title`, `og:image`, `og:type="article"`) matches the frontmatter values.

5. **Automated Unit Testing**:
   Write a test verifying frontmatter parsing and schema rejection:
   ```typescript
   // __tests__/content.test.ts
   import { describe, it, expect } from "vitest";
   import { PostFrontmatterSchema } from "@/lib/content-schema";

   describe("PostFrontmatterSchema", () => {
     it("validates compliant frontmatter", () => {
       const valid = {
         title: "Test Post",
         description: "A description of the post",
         publishedAt: "2026-03-01",
         author: { name: "Author", avatar: "/avatar.png" },
       };
       expect(() => PostFrontmatterSchema.parse(valid)).not.toThrow();
     });

     it("rejects invalid dates and missing titles", () => {
       const invalid = {
         title: "",
         publishedAt: "invalid-date",
       };
       expect(() => PostFrontmatterSchema.parse(invalid)).toThrow();
     });
   });
   ```
