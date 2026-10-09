import { RouterProvider } from 'react-router-dom';
import { router } from './routes';

/** Application root: router only; providers (query client) live in `main.tsx`. */
export function App() {
  return <RouterProvider router={router} />;
}
