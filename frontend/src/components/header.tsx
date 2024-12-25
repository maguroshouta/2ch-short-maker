import Link from "next/link";

export default function Header() {
	return (
		<header className="w-full p-4 border text-2xl flex justify-between items-center">
			<Link href="/">
				<h1 className="font-bold">2ch ショートメーカー</h1>
			</Link>
		</header>
	);
}
