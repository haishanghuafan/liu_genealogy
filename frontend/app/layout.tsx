import type { Metadata } from "next";
import "./globals.css";
import { ClientProvider } from "@/components/ClientProvider";

export const metadata: Metadata = {
  title: "族谱云 | 传承家族记忆",
  description: "现代化的多家族族谱管理平台。族谱树可视化、成员管理、历史记录，让每个家族都能拥有专属的数字族谱。",
  keywords: ["族谱", "家谱", "家族", "族谱管理", "Family Tree", "Genealogy"],
  authors: [{ name: "族谱云" }],
  icons: {
    icon: [
      {
        url: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📜</text></svg>",
        type: "image/svg+xml",
      },
    ],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" className="scroll-smooth">
      <body className="font-sans antialiased">
        <ClientProvider>
          {children}
        </ClientProvider>
      </body>
    </html>
  );
}
