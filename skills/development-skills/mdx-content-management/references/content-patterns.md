# MDX Content Patterns & Architectural Reference

This reference guide provides production-ready code examples, configuration blueprints, and reusable architectural patterns for building content-driven applications with MDX.

---

## 1. MDX File Structure Examples

### 1.1 Complete Blog Post with Rich Components

Save as `content/posts/optimizing-web-performance.mdx`:

```mdx
---
title: "Optimizing Web Performance with Modern Asset Pipelines"
description: "A comprehensive guide to code splitting, modern image delivery, and critical CSS in production web apps."
publishedAt: "2026-03-15"
updatedAt: "2026-03-20"
coverImage: "/images/blog/performance-hero.webp"
coverImageAlt: "Abstract visual representation of network performance metrics"
category: "Engineering"
tags:
  - Performance
  - WebDev
  - Architecture
  - Nextjs
author:
  name: "Alex Morgan"
  role: "Lead Platform Engineer"
  avatar: "/images/authors/alex.webp"
draft: false
featured: true
---

Web performance directly influences user retention, conversion rates, and search rankings. In this post, we break down actionable patterns to streamline your frontend asset pipeline.

<Callout type="info" title="Prerequisites">
Before following this walkthrough, ensure your environment runs Node.js 20+ and uses an ESM-compatible bundler.
</Callout>

## The Critical Rendering Path

When a client requests a page, the browser constructs the DOM, CSSOM, and render tree before executing paint operations.

| Metric | Target (Good) | Needs Improvement | Poor |
| :--- | :--- | :--- | :--- |
| **LCP** (Largest Contentful Paint) | &le; 2.5s | 2.5s - 4.0s | > 4.0s |
| **FID / INP** (Interaction to Next Paint) | &le; 200ms | 200ms - 500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | &le; 0.1 | 0.1 - 0.25 | > 0.25 |

### Asset Delivery Strategies

To minimize render-blocking resources:

1. Defer non-critical JavaScript.
2. In-line above-the-fold critical CSS.
3. Preload priority fonts and hero assets.

```typescript title="lib/asset-loader.ts" {3-5,9}
import { cache } from "react";

export const preloadCriticalFont = cache((fontUrl: string) => {
  // Preload priority webfont during SSR
  return `<link rel="preload" href="${fontUrl}" as="font" type="font/woff2" crossorigin="anonymous" />`;
});

export function generateResourceHints(urls: string[]): string[] {
  return urls.map((url) => `<link rel="dns-prefetch" href="${url}" />`);
}
```

<Tabs defaultValue="nextjs">
  <TabItem value="nextjs" label="Next.js App Router">
    ```tsx title="app/layout.tsx"
    import { Inter } from "next/font/google";

    const inter = Inter({ subsets: ["latin"], display: "swap" });

    export default function RootLayout({ children }: { children: React.ReactNode }) {
      return (
        <html lang="en" className={inter.className}>
          <body>{children}</body>
        </html>
      );
    }
    ```
  </TabItem>
  <TabItem value="standard" label="Standard HTML">
    ```html title="index.html"
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    ```
  </TabItem>
</Tabs>

## Image Optimization Comparison

Use modern WebP or AVIF formats paired with responsive dimensions:

```tsx
<Image
  src="/images/blog/performance-hero.webp"
  alt="Performance pipeline diagram"
  width={800}
  height={450}
  priority
/>
```

<Callout type="warning" title="Watch Out for CLS">
Always supply explicit `width` and `height` attributes or use aspect-ratio containers when embedding images to prevent layout reflows during loading.
</Callout>

## Interactive Benchmark

Below is a live benchmark demo rendered directly inside this MDX article:

<InteractiveBenchmark initialRuns={500} targetLatency={16} />

## Summary and Next Steps

- Audit pages using Lighthouse CLI in CI/CD.
- Monitor real user metrics (RUM) using Web Vitals APIs.
- Enforce bundle budgets on production builds.
```

---

### 1.2 Technical Documentation Page

Save as `content/docs/authentication/jwt-flow.mdx`:

```mdx
---
title: "JWT Authentication Flow"
description: "Implementation details and security considerations for stateless JSON Web Token auth."
section: "Authentication"
order: 3
---

# JWT Authentication Flow

Stateless token authentication allows APIs to verify incoming requests without consulting a persistent session database on every operation.

<StepGuide>
  <Step number={1} title="Client Handshake">
    The client transmits credentials (`username` + `password`) over HTTPS to `/api/v1/auth/login`.
  </Step>
  <Step number={2} title="Token Issuance">
    The authentication server validates credentials, generates an access token (short TTL: 15 minutes) and a refresh token (longer TTL: 7 days), and stores the refresh token in an `HttpOnly`, `Secure`, `SameSite=Strict` cookie.
  </Step>
  <Step number={3} title="Subsequent Requests">
    The client attaches the access token in the `Authorization: Bearer <token>` header for protected endpoints.
  </Step>
</StepGuide>

<Callout type="danger" title="Security Advisory">
Never persist access tokens or refresh tokens in `localStorage` or `sessionStorage` due to susceptibility to Cross-Site Scripting (XSS) extraction.
</Callout>
```

---

## 2. Content Collection & Engine Configurations

### 2.1 Velite Configuration (`velite.config.ts`)

Velite provides build-time schema validation, TypeScript type generation, and remark/rehype processing with zero runtime overhead.

```typescript
import { defineConfig, defineCollection, s } from "velite";
import rehypeSlug from "rehype-slug";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypePrettyCode from "rehype-pretty-code";
import remarkGfm from "remark-gfm";
import readingTime from "reading-time";

const posts = defineCollection({
  name: "Post",
  pattern: "posts/**/*.mdx",
  schema: s
    .object({
      title: s.string().max(100),
      description: s.string().max(200),
      publishedAt: s.isodate(),
      updatedAt: s.isodate().optional(),
      slug: s.path(),
      coverImage: s.string().optional(),
      coverImageAlt: s.string().optional(),
      category: s.string().default("General"),
      tags: s.array(s.string()).default([]),
      draft: s.boolean().default(false),
      featured: s.boolean().default(false),
      author: s.object({
        name: s.string(),
        role: s.string(),
        avatar: s.string(),
      }),
      body: s.mdx(),
      raw: s.raw(),
    })
    .transform((data) => ({
      ...data,
      slugAsParams: data.slug.replace(/^posts\//, ""),
      readingMinutes: Math.ceil(readingTime(data.raw).minutes),
    })),
});

const docs = defineCollection({
  name: "Doc",
  pattern: "docs/**/*.mdx",
  schema: s
    .object({
      title: s.string().max(120),
      description: s.string().max(250),
      section: s.string(),
      order: s.number().default(0),
      slug: s.path(),
      body: s.mdx(),
    })
    .transform((data) => ({
      ...data,
      slugAsParams: data.slug.replace(/^docs\//, ""),
    })),
});

export default defineConfig({
  root: "content",
  output: {
    data: ".velite",
    assets: "public/static",
    base: "/static/",
    name: "[name]-[hash:6].[ext]",
    clean: true,
  },
  collections: { posts, docs },
  mdx: {
    remarkPlugins: [remarkGfm],
    rehypePlugins: [
      rehypeSlug,
      [
        rehypePrettyCode,
        {
          theme: "github-dark",
          keepBackground: false,
          onVisitLine(node: any) {
            if (node.children.length === 0) {
              node.children = [{ type: "text", value: " " }];
            }
          },
          onVisitHighlightedLine(node: any) {
            node.properties.className = ["line--highlighted"];
          },
          onVisitHighlightedWord(node: any) {
            node.properties.className = ["word--highlighted"];
          },
        },
      ],
      [
        rehypeAutolinkHeadings,
        {
          behavior: "wrap",
          properties: {
            className: ["subheading-anchor"],
            ariaLabel: "Link to section",
          },
        },
      ],
    ],
  },
});
```

---

### 2.2 Native React Server Components Engine (`next-mdx-remote/rsc`)

For Next.js App Router applications requiring zero client bundle overhead for static Markdown parsing:

```typescript
// lib/mdx.ts
import fs from "node:fs/promises";
import path from "node:path";
import matter from "gray-matter";
import { z } from "zod";
import readingTime from "reading-time";

const CONTENT_DIR = path.join(process.cwd(), "content/posts");

export const PostFrontmatterSchema = z.object({
  title: z.string().min(1),
  description: z.string().min(1),
  publishedAt: z.string(),
  updatedAt: z.string().optional(),
  coverImage: z.string().optional(),
  coverImageAlt: z.string().optional(),
  category: z.string().default("General"),
  tags: z.array(z.string()).default([]),
  draft: z.boolean().default(false),
  featured: z.boolean().default(false),
  author: z.object({
    name: z.string(),
    role: z.string(),
    avatar: z.string(),
  }),
});

export type PostFrontmatter = z.infer<typeof PostFrontmatterSchema>;

export interface PostItem {
  slug: string;
  frontmatter: PostFrontmatter;
  content: string;
  readingMinutes: number;
}

export async function getPostBySlug(slug: string): Promise<PostItem | null> {
  const normalizedSlug = slug.replace(/\.mdx$/, "");
  const filePath = path.join(CONTENT_DIR, `${normalizedSlug}.mdx`);

  try {
    const rawFile = await fs.readFile(filePath, "utf-8");
    const { data, content } = matter(rawFile);
    const parsedFrontmatter = PostFrontmatterSchema.parse(data);
    const stats = readingTime(content);

    return {
      slug: normalizedSlug,
      frontmatter: parsedFrontmatter,
      content,
      readingMinutes: Math.ceil(stats.minutes),
    };
  } catch (error) {
    return null;
  }
}

export async function getAllPosts(includeDrafts = false): Promise<PostItem[]> {
  try {
    const entries = await fs.readdir(CONTENT_DIR, { withFileTypes: true });
    const mdxFiles = entries.filter(
      (entry) => entry.isFile() && entry.name.endsWith(".mdx")
    );

    const posts = await Promise.all(
      mdxFiles.map(async (file) => {
        const slug = file.name.replace(/\.mdx$/, "");
        return getPostBySlug(slug);
      })
    );

    return posts
      .filter((post): post is PostItem => post !== null)
      .filter((post) => (includeDrafts ? true : !post.frontmatter.draft))
      .sort((a, b) =>
        new Date(b.frontmatter.publishedAt).getTime() -
        new Date(a.frontmatter.publishedAt).getTime()
      );
  } catch {
    return [];
  }
}
```

---

### 2.3 `@next/mdx` Pipeline Configuration

`next.config.mjs` setup with remark and rehype plugins:

```javascript
// next.config.mjs
import createMDX from "@next/mdx";
import remarkGfm from "remark-gfm";
import rehypeSlug from "rehype-slug";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypePrettyCode from "rehype-pretty-code";

/** @type {import('next').NextConfig} */
const nextConfig = {
  pageExtensions: ["js", "jsx", "md", "mdx", "ts", "tsx"],
  images: {
    formats: ["image/avif", "image/webp"],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
    ],
  },
};

const withMDX = createMDX({
  options: {
    remarkPlugins: [remarkGfm],
    rehypePlugins: [
      rehypeSlug,
      [
        rehypePrettyCode,
        {
          theme: "github-dark",
          keepBackground: false,
        },
      ],
      [
        rehypeAutolinkHeadings,
        {
          behavior: "wrap",
          properties: { className: ["heading-anchor"] },
        },
      ],
    ],
  },
});

export default withMDX(nextConfig);
```

---

## 3. Custom Component Mapping Catalog

Create `components/mdx/mdx-components.tsx` with production UI patterns:

```tsx
import React, { ComponentPropsWithoutRef } from "react";
import Image, { ImageProps } from "next/image";
import Link from "next/link";
import dynamic from "next/dynamic";

// Dynamic import for heavy client-only interactive component
const InteractiveBenchmark = dynamic(
  () => import("@/components/mdx/interactive-benchmark"),
  {
    loading: () => (
      <div className="p-6 my-4 border rounded-lg bg-neutral-900/50 animate-pulse text-sm text-neutral-400">
        Loading interactive benchmark...
      </div>
    ),
    ssr: false,
  }
);

// Callout / Alert Component
interface CalloutProps {
  type?: "info" | "warning" | "danger" | "success";
  title?: string;
  children: React.ReactNode;
}

export function Callout({ type = "info", title, children }: CalloutProps) {
  const styles = {
    info: "border-blue-500/40 bg-blue-500/10 text-blue-200",
    warning: "border-amber-500/40 bg-amber-500/10 text-amber-200",
    danger: "border-red-500/40 bg-red-500/10 text-red-200",
    success: "border-emerald-500/40 bg-emerald-500/10 text-emerald-200",
  }[type];

  return (
    <aside className={`my-6 rounded-lg border-l-4 p-4 ${styles}`} role="note">
      {title && <h5 className="font-semibold mb-1 text-sm tracking-wide">{title}</h5>}
      <div className="text-sm leading-relaxed text-inherit [&>p]:m-0">{children}</div>
    </aside>
  );
}

// Accessible Tabs Implementation
interface TabsProps {
  defaultValue: string;
  children: React.ReactElement<TabItemProps>[];
}

interface TabItemProps {
  value: string;
  label: string;
  children: React.ReactNode;
}

export function TabItem({ children }: TabItemProps) {
  return <div>{children}</div>;
}

export function Tabs({ defaultValue, children }: TabsProps) {
  const items = React.Children.toArray(children) as React.ReactElement<TabItemProps>[];
  const [activeTab, setActiveTab] = React.useState(defaultValue || items[0]?.props.value);

  return (
    <div className="my-6 border border-neutral-800 rounded-lg overflow-hidden bg-neutral-950">
      <div className="flex border-b border-neutral-800 bg-neutral-900/50">
        {items.map((item) => (
          <button
            key={item.props.value}
            onClick={() => setActiveTab(item.props.value)}
            className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
              activeTab === item.props.value
                ? "border-blue-500 text-white bg-neutral-800/40"
                : "border-transparent text-neutral-400 hover:text-neutral-200"
            }`}
          >
            {item.props.label}
          </button>
        ))}
      </div>
      <div className="p-4">
        {items.find((item) => item.props.value === activeTab)?.props.children}
      </div>
    </div>
  );
}

// Responsive Next.js Image with Fallback and Caption
export function MdxImage({
  src,
  alt = "",
  width,
  height,
  ...props
}: ImageProps) {
  return (
    <figure className="my-8">
      <div className="relative overflow-hidden rounded-lg border border-neutral-800">
        <Image
          src={src}
          alt={alt}
          width={width || 1200}
          height={height || 630}
          className="w-full h-auto object-cover"
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
          {...props}
        />
      </div>
      {alt && (
        <figcaption className="mt-2 text-center text-xs text-neutral-400">
          {alt}
        </figcaption>
      )}
    </figure>
  );
}

// Code Block with Copy Button
export function CodeBlock({
  children,
  className,
  ...props
}: ComponentPropsWithoutRef<"pre">) {
  const [copied, setCopied] = React.useState(false);
  const textRef = React.useRef<HTMLPreElement>(null);

  const handleCopy = async () => {
    if (textRef.current) {
      await navigator.clipboard.writeText(textRef.current.innerText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="relative group my-4">
      <pre
        ref={textRef}
        className={`p-4 rounded-lg bg-neutral-950 border border-neutral-800 overflow-x-auto text-sm ${
          className || ""
        }`}
        {...props}
      >
        {children}
      </pre>
      <button
        onClick={handleCopy}
        aria-label="Copy code"
        className="absolute top-2 right-2 px-2 py-1 text-xs rounded bg-neutral-800/80 text-neutral-300 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-neutral-700"
      >
        {copied ? "Copied!" : "Copy"}
      </button>
    </div>
  );
}

// Export Complete Component Map
export const mdxComponents = {
  h1: (props: ComponentPropsWithoutRef<"h1">) => (
    <h1 className="text-3xl font-extrabold tracking-tight mt-10 mb-4" {...props} />
  ),
  h2: (props: ComponentPropsWithoutRef<"h2">) => (
    <h2 className="text-2xl font-bold tracking-tight mt-8 mb-3 border-b border-neutral-800 pb-2" {...props} />
  ),
  h3: (props: ComponentPropsWithoutRef<"h3">) => (
    <h3 className="text-xl font-semibold tracking-tight mt-6 mb-2" {...props} />
  ),
  p: (props: ComponentPropsWithoutRef<"p">) => (
    <p className="leading-7 my-4 text-neutral-300" {...props} />
  ),
  a: ({ href = "", children, ...props }: ComponentPropsWithoutRef<"a">) => {
    const isInternal = href.startsWith("/") || href.startsWith("#");
    if (isInternal) {
      return (
        <Link href={href} className="text-blue-400 hover:underline font-medium" {...props}>
          {children}
        </Link>
      );
    }
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-400 hover:underline font-medium inline-flex items-center gap-1"
        {...props}
      >
        {children}
      </a>
    );
  },
  ul: (props: ComponentPropsWithoutRef<"ul">) => (
    <ul className="list-disc pl-6 my-4 space-y-2 text-neutral-300" {...props} />
  ),
  ol: (props: ComponentPropsWithoutRef<"ol">) => (
    <ol className="list-decimal pl-6 my-4 space-y-2 text-neutral-300" {...props} />
  ),
  blockquote: (props: ComponentPropsWithoutRef<"blockquote">) => (
    <blockquote className="border-l-4 border-neutral-600 pl-4 my-4 italic text-neutral-400" {...props} />
  ),
  table: (props: ComponentPropsWithoutRef<"table">) => (
    <div className="overflow-x-auto my-6 border border-neutral-800 rounded-lg">
      <table className="min-w-full divide-y divide-neutral-800 text-sm text-left" {...props} />
    </div>
  ),
  th: (props: ComponentPropsWithoutRef<"th">) => (
    <th className="bg-neutral-900 px-4 py-3 font-semibold text-neutral-200" {...props} />
  ),
  td: (props: ComponentPropsWithoutRef<"td">) => (
    <td className="px-4 py-3 border-t border-neutral-800/50 text-neutral-300" {...props} />
  ),
  pre: CodeBlock,
  img: (props: any) => <MdxImage {...props} />,
  Image: MdxImage,
  Callout,
  Tabs,
  TabItem,
  InteractiveBenchmark,
};
```

---

## 4. Blog Post Template Patterns

### 4.1 Next.js App Router Page Implementation (`app/blog/[slug]/page.tsx`)

```tsx
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { MDXRemote } from "next-mdx-remote/rsc";
import rehypeSlug from "rehype-slug";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypePrettyCode from "rehype-pretty-code";
import remarkGfm from "remark-gfm";

import { getPostBySlug, getAllPosts } from "@/lib/mdx";
import { mdxComponents } from "@/components/mdx/mdx-components";
import { TableOfContents } from "@/components/blog/table-of-contents";
import { extractHeadings } from "@/lib/toc";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const posts = await getAllPosts();
  return posts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPostBySlug(slug);

  if (!post) {
    return { title: "Post Not Found" };
  }

  const { title, description, publishedAt, updatedAt, coverImage, tags, author } = post.frontmatter;
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";
  const postUrl = `${siteUrl}/blog/${slug}`;
  const ogImageUrl = coverImage ? `${siteUrl}${coverImage}` : `${siteUrl}/api/og?title=${encodeURIComponent(title)}`;

  return {
    title: `${title} | Tech Blog`,
    description,
    authors: [{ name: author.name }],
    keywords: tags,
    alternates: {
      canonical: postUrl,
    },
    openGraph: {
      title,
      description,
      type: "article",
      publishedTime: publishedAt,
      modifiedTime: updatedAt || publishedAt,
      url: postUrl,
      images: [
        {
          url: ogImageUrl,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [ogImageUrl],
    },
  };
}

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params;
  const post = await getPostBySlug(slug);

  if (!post) {
    notFound();
  }

  const headings = extractHeadings(post.content);
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";

  // Structured Data (JSON-LD)
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.frontmatter.title,
    description: post.frontmatter.description,
    datePublished: post.frontmatter.publishedAt,
    dateModified: post.frontmatter.updatedAt || post.frontmatter.publishedAt,
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": `${siteUrl}/blog/${slug}`,
    },
    author: {
      "@type": "Person",
      name: post.frontmatter.author.name,
      jobTitle: post.frontmatter.author.role,
    },
    image: post.frontmatter.coverImage ? `${siteUrl}${post.frontmatter.coverImage}` : undefined,
  };

  return (
    <article className="max-w-6xl mx-auto px-4 py-12">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <header className="max-w-3xl mx-auto mb-10 text-center">
        <div className="flex items-center justify-center gap-2 mb-4">
          <span className="px-3 py-1 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
            {post.frontmatter.category}
          </span>
          <span className="text-xs text-neutral-400">
            {post.readingMinutes} min read
          </span>
        </div>

        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white mb-6">
          {post.frontmatter.title}
        </h1>

        <p className="text-lg text-neutral-400 mb-6">
          {post.frontmatter.description}
        </p>

        <div className="flex items-center justify-center gap-3">
          <Image
            src={post.frontmatter.author.avatar}
            alt={post.frontmatter.author.name}
            width={40}
            height={40}
            className="rounded-full ring-2 ring-neutral-700"
          />
          <div className="text-left text-sm">
            <p className="font-semibold text-neutral-200">{post.frontmatter.author.name}</p>
            <p className="text-neutral-500">
              {new Date(post.frontmatter.publishedAt).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </p>
          </div>
        </div>
      </header>

      {post.frontmatter.coverImage && (
        <div className="max-w-4xl mx-auto mb-12 relative aspect-[16/9] overflow-hidden rounded-xl border border-neutral-800">
          <Image
            src={post.frontmatter.coverImage}
            alt={post.frontmatter.coverImageAlt || post.frontmatter.title}
            fill
            priority
            className="object-cover"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_260px] gap-12 max-w-5xl mx-auto">
        <main className="min-w-0 prose prose-invert prose-neutral max-w-none">
          <MDXRemote
            source={post.content}
            components={mdxComponents}
            options={{
              mdxOptions: {
                remarkPlugins: [remarkGfm],
                rehypePlugins: [
                  rehypeSlug,
                  [
                    rehypePrettyCode,
                    {
                      theme: "github-dark",
                      keepBackground: false,
                    },
                  ],
                  [
                    rehypeAutolinkHeadings,
                    {
                      behavior: "wrap",
                      properties: { className: ["subheading-anchor"] },
                    },
                  ],
                ],
              },
            }}
          />
        </main>

        <aside className="hidden lg:block">
          <div className="sticky top-24">
            <TableOfContents headings={headings} />
          </div>
        </aside>
      </div>

      <footer className="max-w-3xl mx-auto mt-16 pt-8 border-t border-neutral-800">
        <div className="flex flex-wrap gap-2">
          {post.frontmatter.tags.map((tag) => (
            <Link
              key={tag}
              href={`/blog/tags/${encodeURIComponent(tag.toLowerCase())}`}
              className="text-xs px-2.5 py-1 rounded bg-neutral-800 text-neutral-300 hover:bg-neutral-700 transition"
            >
              #{tag}
            </Link>
          ))}
        </div>
      </footer>
    </article>
  );
}
```

---

### 4.2 Table of Contents Parser (`lib/toc.ts`)

```typescript
export interface TocHeading {
  id: string;
  text: string;
  level: number;
}

export function extractHeadings(markdown: string): TocHeading[] {
  const headingRegex = /^(#{2,4})\s+(.*)$/gm;
  const headings: TocHeading[] = [];
  let match;

  while ((match = headingRegex.exec(markdown)) !== null) {
    const level = match[1].length;
    const rawText = match[2].trim();
    // Strip inline markdown symbols (links, bold, code)
    const text = rawText
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
      .replace(/[`*_]/g, "");

    const id = text
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .replace(/\s+/g, "-");

    headings.push({ id, text, level });
  }

  return headings;
}
```

---

## 5. Category and Tag Taxonomy Systems

### 5.1 Taxonomy Utilities (`lib/taxonomy.ts`)

```typescript
import { getAllPosts, PostItem } from "@/lib/mdx";

export interface TagCount {
  name: string;
  slug: string;
  count: number;
}

export async function getAllTags(): Promise<TagCount[]> {
  const posts = await getAllPosts();
  const tagMap = new Map<string, number>();

  for (const post of posts) {
    for (const tag of post.frontmatter.tags) {
      const normalized = tag.trim();
      tagMap.set(normalized, (tagMap.get(normalized) || 0) + 1);
    }
  }

  return Array.from(tagMap.entries())
    .map(([name, count]) => ({
      name,
      slug: name.toLowerCase().replace(/\s+/g, "-"),
      count,
    }))
    .sort((a, b) => b.count - a.count);
}

export async function getPostsByTag(tagSlug: string): Promise<PostItem[]> {
  const posts = await getAllPosts();
  return posts.filter((post) =>
    post.frontmatter.tags.some(
      (t) => t.toLowerCase().replace(/\s+/g, "-") === tagSlug.toLowerCase()
    )
  );
}
```

### 5.2 Dynamic Tag Route (`app/blog/tags/[tag]/page.tsx`)

```tsx
import { notFound } from "next/navigation";
import Link from "next/link";
import { getAllTags, getPostsByTag } from "@/lib/taxonomy";

interface TagPageProps {
  params: Promise<{ tag: string }>;
}

export async function generateStaticParams() {
  const tags = await getAllTags();
  return tags.map((t) => ({ tag: t.slug }));
}

export default async function TagPage({ params }: TagPageProps) {
  const { tag } = await params;
  const posts = await getPostsByTag(tag);

  if (posts.length === 0) {
    notFound();
  }

  return (
    <section className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-2">Tag: #{tag}</h1>
      <p className="text-neutral-400 mb-8">{posts.length} article(s) found</p>

      <div className="space-y-6">
        {posts.map((post) => (
          <article key={post.slug} className="p-6 border border-neutral-800 rounded-lg hover:border-neutral-700 transition">
            <span className="text-xs text-neutral-500">
              {new Date(post.frontmatter.publishedAt).toLocaleDateString()}
            </span>
            <h2 className="text-2xl font-bold mt-1 mb-2">
              <Link href={`/blog/${post.slug}`} className="hover:text-blue-400">
                {post.frontmatter.title}
              </Link>
            </h2>
            <p className="text-neutral-400 text-sm">{post.frontmatter.description}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
```

---

## 6. Pagination Patterns for Content

### 6.1 Static Chunked Pagination (`app/blog/page/[page]/page.tsx`)

```tsx
import { notFound } from "next/navigation";
import Link from "next/link";
import { getAllPosts } from "@/lib/mdx";

const POSTS_PER_PAGE = 10;

interface PageRouteProps {
  params: Promise<{ page: string }>;
}

export async function generateStaticParams() {
  const posts = await getAllPosts();
  const totalPages = Math.ceil(posts.length / POSTS_PER_PAGE);

  return Array.from({ length: totalPages }, (_, i) => ({
    page: String(i + 1),
  }));
}

export default async function PaginatedBlogPage({ params }: PageRouteProps) {
  const { page } = await params;
  const currentPage = parseInt(page, 10);

  if (isNaN(currentPage) || currentPage < 1) {
    notFound();
  }

  const posts = await getAllPosts();
  const totalPages = Math.ceil(posts.length / POSTS_PER_PAGE);

  if (currentPage > totalPages) {
    notFound();
  }

  const paginatedPosts = posts.slice(
    (currentPage - 1) * POSTS_PER_PAGE,
    currentPage * POSTS_PER_PAGE
  );

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-4xl font-extrabold mb-8">Articles (Page {currentPage})</h1>

      <div className="space-y-6">
        {paginatedPosts.map((post) => (
          <article key={post.slug} className="border-b border-neutral-800 pb-6">
            <h2 className="text-2xl font-bold mb-2">
              <Link href={`/blog/${post.slug}`} className="hover:text-blue-400">
                {post.frontmatter.title}
              </Link>
            </h2>
            <p className="text-neutral-400 text-sm mb-2">{post.frontmatter.description}</p>
            <span className="text-xs text-neutral-500">
              {post.readingMinutes} min read &bull; {post.frontmatter.publishedAt}
            </span>
          </article>
        ))}
      </div>

      {/* Pagination Navigation */}
      <nav className="flex items-center justify-between mt-12 pt-6 border-t border-neutral-800" aria-label="Pagination">
        {currentPage > 1 ? (
          <Link
            href={currentPage === 2 ? "/blog" : `/blog/page/${currentPage - 1}`}
            className="px-4 py-2 text-sm border border-neutral-700 rounded hover:bg-neutral-800"
          >
            &larr; Previous
          </Link>
        ) : <div />}

        <span className="text-sm text-neutral-400">
          Page {currentPage} of {totalPages}
        </span>

        {currentPage < totalPages ? (
          <Link
            href={`/blog/page/${currentPage + 1}`}
            className="px-4 py-2 text-sm border border-neutral-700 rounded hover:bg-neutral-800"
          >
            Next &rarr;
          </Link>
        ) : <div />}
      </nav>
    </div>
  );
}
```

---

## 7. Search Integration Patterns

### 7.1 Build-Time Search Index Generation (`scripts/build-search-index.mjs`)

Generate a lightweight JSON index during build time to avoid client-side bloat:

```javascript
import fs from "node:fs/promises";
import path from "node:path";
import matter from "gray-matter";

const CONTENT_DIR = path.join(process.cwd(), "content/posts");
const OUTPUT_FILE = path.join(process.cwd(), "public/search-index.json");

async function generateIndex() {
  const files = await fs.readdir(CONTENT_DIR);
  const mdxFiles = files.filter((f) => f.endsWith(".mdx"));

  const records = [];

  for (const filename of mdxFiles) {
    const raw = await fs.readFile(path.join(CONTENT_DIR, filename), "utf-8");
    const { data, content } = matter(raw);

    if (data.draft) continue;

    const slug = filename.replace(/\.mdx$/, "");
    // Clean markdown syntax for plain-text search index
    const plainText = content
      .replace(/```[\s\S]*?```/g, "")
      .replace(/<[^>]+>/g, "")
      .replace(/[#*_`\[\]]/g, "")
      .slice(0, 1500); // Index first 1500 characters of content body

    records.push({
      slug,
      title: data.title,
      description: data.description,
      tags: data.tags || [],
      category: data.category || "General",
      content: plainText,
    });
  }

  await fs.writeFile(OUTPUT_FILE, JSON.stringify(records));
  console.log(`Search index generated with ${records.length} documents.`);
}

generateIndex();
```

---

### 7.2 Client-Side Command Palette Search (`components/search/search-dialog.tsx`)

```tsx
"use client";

import React, { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";

interface SearchDocument {
  slug: string;
  title: string;
  description: string;
  tags: string[];
  category: string;
}

export function SearchDialog() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [docs, setDocs] = useState<SearchDocument[]>([]);
  const router = useRouter();

  useEffect(() => {
    // Keyboard shortcut handler: Cmd+K / Ctrl+K
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      } else if (e.key === "Escape") {
        setIsOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (isOpen && docs.length === 0) {
      fetch("/search-index.json")
        .then((res) => res.json())
        .then((data) => setDocs(data))
        .catch(console.error);
    }
  }, [isOpen, docs.length]);

  const results = useMemo(() => {
    if (!query.trim()) return [];
    const q = query.toLowerCase();

    return docs.filter((item) =>
      item.title.toLowerCase().includes(q) ||
      item.description.toLowerCase().includes(q) ||
      item.tags.some((t) => t.toLowerCase().includes(q))
    ).slice(0, 8);
  }, [query, docs]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-start justify-center pt-24 px-4">
      <div className="w-full max-w-xl bg-neutral-900 border border-neutral-800 rounded-xl shadow-2xl overflow-hidden">
        <div className="p-4 border-b border-neutral-800">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search articles, topics, or guides..."
            autoFocus
            className="w-full bg-transparent text-white placeholder-neutral-500 focus:outline-none text-base"
          />
        </div>

        <div className="max-h-96 overflow-y-auto p-2">
          {results.length > 0 ? (
            results.map((item) => (
              <button
                key={item.slug}
                onClick={() => {
                  setIsOpen(false);
                  router.push(`/blog/${item.slug}`);
                }}
                className="w-full text-left p-3 rounded-lg hover:bg-neutral-800 transition flex flex-col gap-1"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white text-sm">{item.title}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-neutral-700 text-neutral-300">
                    {item.category}
                  </span>
                </div>
                <p className="text-xs text-neutral-400 line-clamp-1">{item.description}</p>
              </button>
            ))
          ) : query.trim() ? (
            <p className="p-4 text-center text-sm text-neutral-500">No matching articles found.</p>
          ) : (
            <p className="p-4 text-center text-xs text-neutral-500">Type to search content...</p>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

## 8. Automated RSS and Atom Feed Generation

Create `app/rss.xml/route.ts` to statically serve valid RSS 2.0:

```typescript
import { getAllPosts } from "@/lib/mdx";

export async function GET() {
  const posts = await getAllPosts();
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";

  const feedItems = posts
    .map((post) => {
      const url = `${siteUrl}/blog/${post.slug}`;
      return `
    <item>
      <title><![CDATA[${post.frontmatter.title}]]></title>
      <link>${url}</link>
      <guid isPermaLink="true">${url}</guid>
      <description><![CDATA[${post.frontmatter.description}]]></description>
      <pubDate>${new Date(post.frontmatter.publishedAt).toUTCString()}</pubDate>
      <author>${post.frontmatter.author.name}</author>
      ${post.frontmatter.tags.map((tag) => `<category>${tag}</category>`).join("\n      ")}
    </item>`;
    })
    .join("");

  const rssFeed = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Engineering &amp; Architecture Blog</title>
    <link>${siteUrl}/blog</link>
    <description>Articles and guides on modern software engineering.</description>
    <language>en-US</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${siteUrl}/rss.xml" rel="self" type="application/rss+xml"/>
    ${feedItems}
  </channel>
</rss>`;

  return new Response(rssFeed.trim(), {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "s-maxage=3600, stale-while-revalidate",
    },
  });
}
```
