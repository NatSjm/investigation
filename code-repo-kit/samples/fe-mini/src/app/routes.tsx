import { createBrowserRouter } from 'react-router-dom';
import { HedgeProposalList, HedgeStressChart } from '@/features/hedges';
import { LoanSchedule } from '@/features/loans';

export const router = createBrowserRouter([
  { path: '/clients/:clientId/hedges', element: <HedgeProposalList clientId="" /> },
  { path: '/clients/:clientId/hedges/:proposalId/stress', element: <HedgeStressChart series={[]} /> },
  { path: '/clients/:clientId/loans', element: <LoanSchedule /> },
]);
