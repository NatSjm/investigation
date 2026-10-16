import { BrowserRouter } from 'react-router-dom';
import { Routing } from '@/routing';

/** Application root: router only; providers (query client) live in `main.tsx`. */
export function App() {
  return (
    <BrowserRouter>
      <Routing />
    </BrowserRouter>
  );
}
