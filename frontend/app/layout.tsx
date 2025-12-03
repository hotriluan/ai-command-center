import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
    title: "AI Command Center - Executive Dashboard",
    description: "Real-time business intelligence dashboard with AI-powered analytics",
    icons: {
        icon: '/favicon.svg',
    },
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className="antialiased">
                {children}
            </body>
        </html>
    );
}
