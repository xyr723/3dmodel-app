import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import type { EvaluationMetrics } from '../types';
import { createBasicScene } from '../threejs/scene';
import { loadAnyModel } from '../threejs/loaders';
import { createOrbitControls } from '../threejs/controls';

export function ModelViewer({ url, onMetrics }: { url?: string; onMetrics?: (m: Partial<EvaluationMetrics>) => void }) {
	const mountRef = useRef<HTMLDivElement | null>(null);
	const [error, setError] = useState<string | undefined>();

	useEffect(() => {
		if (!url || !mountRef.current) return;
		const container = mountRef.current;
		const { scene, camera, renderer, dispose } = createBasicScene(container);

		let animationId = 0;
		const start = performance.now();
		loadAnyModel(url)
			.then((root) => {
				scene.add(root);
				const bbox = new THREE.Box3().setFromObject(root);
				const size = bbox.getSize(new THREE.Vector3());
				const maxDim = Math.max(size.x, size.y, size.z) || 1;
				const scale = 1.0 / maxDim;
				root.scale.setScalar(scale);
				camera.lookAt(new THREE.Vector3());
				onMetrics?.({ isDownloadedRenderable: true, loadTimeMs: performance.now() - start });
			})
			.catch(() => {
				setError('Failed to load model');
				onMetrics?.({ isDownloadedRenderable: false });
			});

		createOrbitControls(camera as any, renderer.domElement);

		const animate = () => {
			animationId = requestAnimationFrame(animate);
			renderer.render(scene, camera);
		};
		animate();

		return () => {
			cancelAnimationFrame(animationId);
			dispose();
		};
	}, [url]);

	return (
		<div style={{ width: '100%', height: '60vh', minHeight: 480, maxHeight: 800, background: '#111', borderRadius: 8 }} ref={mountRef}>
			{!url && <div style={{ color: '#aaa', padding: 12 }}>No model yet</div>}
			{error && <div style={{ color: 'tomato', padding: 12 }}>{error}</div>}
		</div>
	);
} 