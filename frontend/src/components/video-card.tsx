export default function VideoCard({ video }: { video: Video }) {
	return (
		<div className="m-4 relative transition hover:-translate-y-4 cursor-pointer">
			<img
				className="w-64 rounded-xl shadow-md"
				src={`${process.env.NEXT_PUBLIC_API_URL}/api/videos/generated/${video.id}/thumbnail`}
				alt={video.prompt}
			/>
			<div className="flex absolute bottom-4 left-4 bg-white p-2 rounded-xl">
				<p className="overflow-hidden font-bold">{video.prompt}</p>
			</div>
		</div>
	);
}
