# Layouts

## Root layout

Path: `app/layout.tsx`

Renders the HTML document and page children. There is no navigation, shell, or
shared visual layout yet.

```tsx
import type { Metadata } from "next";
export const metadata: Metadata = { title: "Aurorium Mind", description: "Private, evidence-grounded personal assistant" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
```

