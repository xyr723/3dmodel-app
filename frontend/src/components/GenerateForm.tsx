import { useState } from 'react';
import type { GenerationInput, GeneratedModel } from '../types';
import { generateModel } from '../services/meshyClient';

export function GenerateForm({ onResult, onProviderChange }: { onResult: (m: GeneratedModel) => void; onProviderChange?: (provider: 'meshy' | 'sketchfab') => void }) {
	const [promptText, setPromptText] = useState('a low-poly horse');
	const [style, setStyle] = useState('low-poly');
	const [provider, setProvider] = useState<'meshy' | 'sketchfab'>('meshy');
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
				style: provider === 'sketchfab' ? 'sketchfab' : style,
				provider: provider as any,
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
				<div>Provider</div>
				<select value={provider} onChange={(e) => {
					const newProvider = e.target.value as 'meshy' | 'sketchfab';
					setProvider(newProvider);
					onProviderChange?.(newProvider);
				}}>
					<option value="meshy">Meshy (AI Generation)</option>
					<option value="sketchfab">Sketchfab (Model Library)</option>
				</select>
			</label>
			<label>
				<div>Prompt</div>
				<input 
					value={promptText} 
					onChange={(e) => setPromptText(e.target.value)} 
					placeholder={provider === 'sketchfab' ? "Search for models..." : "Describe the object"} 
				/>
			</label>
			{provider === 'meshy' && (
				<label>
					<div>Style</div>
					<select value={style} onChange={(e) => setStyle(e.target.value)}>
						<option value="realistic">realistic</option>
						<option value="low-poly">low-poly</option>
						<option value="stylized">stylized</option>
					</select>
				</label>
			)}
			<label>
				<div>Reference Image (optional)</div>
				<input type="file" accept="image/*" onChange={onImageChange} />
				{imageDataUrl && <img src={imageDataUrl} style={{ maxWidth: 200, display: 'block', marginTop: 8 }} />}
			</label>
			<button type="submit" disabled={loading}>
				{loading ? (provider === 'sketchfab' ? 'Searching...' : 'Generating...') : (provider === 'sketchfab' ? 'Search Models' : 'Generate')}
			</button>
			{error && <div style={{ color: 'tomato' }}>{error}</div>}
		</form>
	);
} 