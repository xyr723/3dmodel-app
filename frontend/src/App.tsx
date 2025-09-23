import { useState } from 'react'
import './App.css'
import GeneratePage from './pages/GeneratePage'
import DashboardPage from './pages/DashboardPage'

export default function App() {
	const [tab, setTab] = useState<'generate' | 'dashboard'>('generate')
	return (
		<div style={{ width: '100%' }}>
			<header className="app-header">
				<button onClick={() => setTab('generate')} disabled={tab==='generate'}>Generate</button>
				<button onClick={() => setTab('dashboard')} disabled={tab==='dashboard'}>Dashboard</button>
			</header>
			<main>
				{tab === 'generate' ? <GeneratePage /> : <DashboardPage />}
			</main>
		</div>
	)
}
