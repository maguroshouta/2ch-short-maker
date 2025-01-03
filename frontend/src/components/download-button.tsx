"use client";

import { Download } from "lucide-react";

export default function DownloadButton({ video }: { video: Video }) {
	async function download() {
		const res = await fetch(
			`${process.env.NEXT_PUBLIC_API_URL}/api/videos/generated/${video.id}`,
		);
		const blob = await res.blob();
		const url = window.URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `${video.id}.mp4`;
		a.click();
	}

	return (
		<span
			onClick={download}
			className="cursor-pointer border bg-white rounded-full"
		>
			<Download className="px-2" size={48} color="#000" />
		</span>
	);
}
