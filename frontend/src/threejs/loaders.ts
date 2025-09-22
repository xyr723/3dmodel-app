import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';

let sharedGltfLoader: GLTFLoader | undefined;
let sharedObjLoader: OBJLoader | undefined;
let sharedStlLoader: STLLoader | undefined;

export function getGLTFLoader(): GLTFLoader {
	if (!sharedGltfLoader) {
		sharedGltfLoader = new GLTFLoader();
	}
	return sharedGltfLoader;
}

export function getOBJLoader(): OBJLoader {
	if (!sharedObjLoader) {
		sharedObjLoader = new OBJLoader();
	}
	return sharedObjLoader;
}

export function getSTLLoader(): STLLoader {
	if (!sharedStlLoader) {
		sharedStlLoader = new STLLoader();
	}
	return sharedStlLoader;
}

export function loadAnyModel(url: string): Promise<THREE.Object3D> {
	const lower = url.split('?')[0].toLowerCase();
	if (lower.endsWith('.glb') || lower.endsWith('.gltf')) {
		return new Promise((resolve, reject) => {
			getGLTFLoader().load(url, (gltf) => resolve(gltf.scene), undefined, (e) => reject(e));
		});
	}
	if (lower.endsWith('.obj')) {
		return new Promise((resolve, reject) => {
			getOBJLoader().load(url, (obj) => resolve(obj), undefined, (e) => reject(e));
		});
	}
	if (lower.endsWith('.stl')) {
		return new Promise((resolve, reject) => {
			getSTLLoader().load(url, (geom) => {
				const material = new THREE.MeshStandardMaterial({ color: 0xcccccc, metalness: 0.0, roughness: 0.9 });
				const mesh = new THREE.Mesh(geom, material);
				mesh.castShadow = true;
				mesh.receiveShadow = true;
				resolve(mesh);
			}, undefined, (e) => reject(e));
		});
	}
	// default try GLTF loader
	return new Promise((resolve, reject) => {
		getGLTFLoader().load(url, (gltf) => resolve(gltf.scene), undefined, (e) => reject(e));
	});
} 