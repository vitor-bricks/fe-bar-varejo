import { useEffect, useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import Shell from './components/Shell';
import Home from './pages/Home';
import Network from './pages/Network';
import Queue from './pages/Queue';
import Agent from './pages/Agent';
import Lakebase from './pages/Lakebase';
import { api } from './lib/api';

export default function App() {
  const [asOf, setAsOf] = useState<string | null>(null);
  useEffect(() => { api.overview().then((o) => setAsOf(o.as_of)).catch(() => undefined); }, []);
  return (
    <Shell asOf={asOf}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/rede" element={<Network />} />
        <Route path="/fila" element={<Queue />} />
        <Route path="/agente" element={<Agent />} />
        <Route path="/lakebase" element={<Lakebase />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  );
}
