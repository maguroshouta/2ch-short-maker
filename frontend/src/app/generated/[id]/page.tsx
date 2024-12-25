export default async function GeneratePage({
	params,
}: { params: { id: string } }) {
	return <div>{params.id}</div>;
}
