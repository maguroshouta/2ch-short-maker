const normalizeBase = (value: string | undefined) => {
	if (!value) {
		return "";
	}
	return value.endsWith("/") ? value.slice(0, -1) : value;
};

export const publicApiUrl = (path: string) => {
	const normalizedPath = path.startsWith("/") ? path : `/${path}`;
	const base = normalizeBase(process.env.NEXT_PUBLIC_API_URL);
	return base ? `${base}${normalizedPath}` : normalizedPath;
};

export const serverApiUrl = (path: string) => {
	const normalizedPath = path.startsWith("/") ? path : `/${path}`;
	const internalBase = normalizeBase(process.env.INTERNAL_API_URL);
	const publicBase = normalizeBase(process.env.NEXT_PUBLIC_API_URL);
	const base = internalBase || publicBase;
	return base ? `${base}${normalizedPath}` : normalizedPath;
};
