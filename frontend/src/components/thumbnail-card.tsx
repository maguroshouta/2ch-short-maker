import Link from "next/link";
import { publicApiUrl } from "@/lib/api-url";

export default function ThumbnailCard({ video }: { video: Video }) {
	return (
		<Link href={`/generated/${video.id}`}>
			<div className="m-4 transition hover:scale-105 cursor-pointer">
				<img
					className="w-64 rounded-xl shadow-md"
					src={publicApiUrl(`/api/videos/${video.id}.jpg`)}
					alt={video.prompt}
				/>
			</div>
		</Link>
	);
}
