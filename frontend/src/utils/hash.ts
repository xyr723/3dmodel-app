export async function hashString(input: string): Promise<string> {
	const encoder = new TextEncoder();
	const data = encoder.encode(input);
	const digest = await crypto.subtle.digest('SHA-256', data);
	const hashArray = Array.from(new Uint8Array(digest));
	return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
} 