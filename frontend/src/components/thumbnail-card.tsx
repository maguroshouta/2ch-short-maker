import Link from "next/link";

export default function ThumbnailCard({ video }: { video: Video }) {
	return (
		<Link href={`/generated/${video.id}`}>
			<div className="m-4 relative transition hover:scale-105 cursor-pointer">
				<img
					className="w-48 rounded-xl shadow-md md:w-64"
					src={`${process.env.NEXT_PUBLIC_API_URL}/api/videos/${video.id}.jpg`}
					alt={video.prompt}
				/>
			</div>
		</Link>
	);
}
