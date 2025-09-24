export async function hashString(input: string): Promise<string> {
	const encoder = new TextEncoder();
	const data = encoder.encode(input);
	// Resolve Web Crypto subtle for browser and Node fallback
	let subtle: SubtleCrypto | undefined = (globalThis as any)?.crypto?.subtle;
	if (!subtle) {
		try {
			// eslint-disable-next-line @typescript-eslint/consistent-type-imports
			const nodeCrypto: typeof import('crypto') = await import('crypto');
			subtle = (nodeCrypto as any)?.webcrypto?.subtle;
		} catch (_) {
			// ignore
		}
	}
	if (!subtle) {
		// Fallback: non-crypto FNV-1a based hash (good enough for cache keying)
		return fnv1aHex128(input);
	}
	const digest = await subtle.digest('SHA-256', data);
	const hashArray = Array.from(new Uint8Array(digest));
	return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}

function fnv1a32(str: string, seed = 0x811c9dc5): number {
	let hash = seed >>> 0;
	for (let i = 0; i < str.length; i++) {
		hash ^= str.charCodeAt(i);
		hash = Math.imul(hash, 0x01000193) >>> 0; // 16777619
	}
	return hash >>> 0;
}

function toHex8(n: number): string {
	return (n >>> 0).toString(16).padStart(8, '0');
}

// Combine two FNV-1a passes (original and reversed) to get 128-bit style hex
function fnv1aHex128(str: string): string {
	const h1 = fnv1a32(str, 0x811c9dc5);
	const h2 = fnv1a32([...str].reverse().join(''), 0x811c9dc5 ^ 0x9e3779b9);
	const h3 = fnv1a32(str + '#', 0x811c9dc5 ^ 0x85ebca6b);
	const h4 = fnv1a32('#' + str, 0x811c9dc5 ^ 0xc2b2ae35);
	return toHex8(h1) + toHex8(h2) + toHex8(h3) + toHex8(h4);
} 