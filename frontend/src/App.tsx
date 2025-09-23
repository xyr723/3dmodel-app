import { useState } from 'react'
import './App.css'
import GeneratePage from './pages/GeneratePage'
import DashboardPage from './pages/DashboardPage'

export default function App() {
	const [tab, setTab] = useState<'generate' | 'dashboard'>('generate')
	return (
		<div style={{ width: '100%' }}>
			<header style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 12, padding: 12, width: '100%', borderBottom: '1px solid #333', boxSizing: 'border-box' }}>
				<button onClick={() => setTab('generate')} disabled={tab==='generate'}>Generate</button>
				<button onClick={() => setTab('dashboard')} disabled={tab==='dashboard'}>Dashboard</button>
			</header>
			<main>
				{tab === 'generate' ? <GeneratePage /> : <DashboardPage />}
			</main>
		</div>
	)
}
