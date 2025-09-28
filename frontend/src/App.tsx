import { useState } from 'react'
import './App.css'
import GeneratePage from './pages/GeneratePage'
import DashboardPage from './pages/DashboardPage'
import SketchfabPage from './pages/SketchfabPage'

export default function App() {
	const [tab, setTab] = useState<'generate' | 'sketchfab' | 'dashboard'>('generate')
	return (
		<div style={{ width: '100%' }}>
			<header className="app-header">
				{/* <button onClick={() => setTab('generate')} disabled={tab==='generate'}>Generate</button> */}
				<button onClick={() => setTab('sketchfab')} disabled={tab==='sketchfab'}>Sketchfab</button>
				{/* <button onClick={() => setTab('dashboard')} disabled={tab==='dashboard'}>Dashboard</button> */}
			</header>
			<main>
				{tab === 'generate' ? <GeneratePage /> : tab === 'sketchfab' ? <SketchfabPage /> : <DashboardPage />}
			</main>
		</div>
	)
}
