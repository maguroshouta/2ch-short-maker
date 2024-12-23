export default function VideoCard({ video }: { video: Video }) {
	return (
		<div className="relative">
			<video
				className="w-64 rounded-lg shadow-lg transition-all hover:shadow-xl hover:scale-110"
				src={`${process.env.NEXT_PUBLIC_API_URL}/api/videos/generated/${video.id}`}
				muted
			/>
			<div className="flex absolute bottom-4 left-4 bg-white p-2 rounded-xl">
				<p className="overflow-hidden font-bold">{video.prompt}</p>
			</div>
		</div>
	);
}
