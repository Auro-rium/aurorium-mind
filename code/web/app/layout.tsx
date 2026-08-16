import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Aurorium Mind",
  description: "A personal environment for evidence-grounded reasoning.",
};

export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
