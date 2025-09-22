import { useEffect, useRef } from 'react';

export function useAnimationFrame(callback: (dt: number) => void) {
	const lastRef = useRef<number>(performance.now());
	const rafRef = useRef<number | null>(null);
	useEffect(() => {
		const loop = () => {
			const now = performance.now();
			const dt = now - lastRef.current;
			lastRef.current = now;
			callback(dt);
			rafRef.current = requestAnimationFrame(loop);
		};
		rafRef.current = requestAnimationFrame(loop);
		return () => {
			if (rafRef.current) cancelAnimationFrame(rafRef.current);
		};
	}, [callback]);
} 