import Link from "next/link";

export default function ThumbnailCard({ video }: { video: Video }) {
	return (
		<Link href={`/generated/${video.id}`}>
			<div className="m-4 relative transition hover:scale-105 cursor-pointer">
				<img
					className="w-48 rounded-xl shadow-md md:w-64"
					src={`${process.env.NEXT_PUBLIC_API_URL}/api/videos/generated/${video.id}/thumbnail`}
					alt={video.prompt}
				/>
				<div className="flex absolute bottom-4 left-4 bg-white p-2 rounded-xl">
					<p className="overflow-hidden font-bold">{video.prompt}</p>
				</div>
			</div>
		</Link>
	);
}
