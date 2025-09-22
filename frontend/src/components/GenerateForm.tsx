import { useState } from 'react';
import type { GenerationInput, GeneratedModel } from '../types';
import { generateModel } from '../services/meshyClient';

export function GenerateForm({ onResult }: { onResult: (m: GeneratedModel) => void }) {
	const [promptText, setPromptText] = useState('a low-poly horse');
	const [style, setStyle] = useState('low-poly');
	const [imageDataUrl, setImageDataUrl] = useState<string | undefined>();
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | undefined>();

	const onImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (!file) return;
		const reader = new FileReader();
		reader.onload = () => setImageDataUrl(reader.result as string);
		reader.readAsDataURL(file);
	};

	const onSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setError(undefined);
		setLoading(true);
		try {
			const input: GenerationInput = {
				promptText,
				referenceImageDataUrl: imageDataUrl,
				style,
			};
			const res = await generateModel(input);
			onResult(res);
		} catch (err: any) {
			setError(err?.message || 'Generation failed');
		} finally {
			setLoading(false);
		}
	};

	return (
		<form onSubmit={onSubmit} style={{ display: 'grid', gap: 12 }}>
			<label>
				<div>Prompt</div>
				<input value={promptText} onChange={(e) => setPromptText(e.target.value)} placeholder="Describe the object" />
			</label>
			<label>
				<div>Style</div>
				<select value={style} onChange={(e) => setStyle(e.target.value)}>
					<option value="realistic">realistic</option>
					<option value="low-poly">low-poly</option>
					<option value="stylized">stylized</option>
				</select>
			</label>
			<label>
				<div>Reference Image (optional)</div>
				<input type="file" accept="image/*" onChange={onImageChange} />
				{imageDataUrl && <img src={imageDataUrl} style={{ maxWidth: 200, display: 'block', marginTop: 8 }} />}
			</label>
			<button type="submit" disabled={loading}>{loading ? 'Generating...' : 'Generate'}</button>
			{error && <div style={{ color: 'tomato' }}>{error}</div>}
		</form>
	);
} 