import type { Metadata } from "next";
import { Noto_Sans_JP } from "next/font/google";
import "./globals.css";
import Header from "@/components/header";

const notoSansJP = Noto_Sans_JP({
	subsets: ["latin"],
});

export const metadata: Metadata = {
	title: "2ch ショートメーカー",
	description: "量産型のショートを生成します",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="ja">
			<body className={`${notoSansJP.className} antialiased`}>
				<Header />
				{children}
			</body>
		</html>
	);
}
