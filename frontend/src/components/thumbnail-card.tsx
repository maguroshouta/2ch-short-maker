import Link from "next/link";

export default function ThumbnailCard({ video }: { video: Video }) {
	return (
		<Link href={`/generated/${video.id}`}>
			<div className="m-4 transition hover:scale-105 cursor-pointer">
				<img
					className="w-64 rounded-xl shadow-md"
					src={`${process.env.NEXT_PUBLIC_API_URL}/api/videos/${video.id}.jpg`}
					alt={video.prompt}
				/>
			</div>
		</Link>
	);
}
