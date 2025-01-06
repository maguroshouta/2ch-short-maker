import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";

export default function Header() {
	return (
		<header className="w-full p-4 border-b text-2xl flex justify-between items-center">
			<Link href="/">
				<h1 className="font-bold">2ch ショートメーカー</h1>
			</Link>
			<ThemeToggle />
		</header>
	);
}
