import { createTRPCReact } from '@trpc/react-query';
// Placeholder type until server router is defined
export type AppRouter = any;

export const trpc = createTRPCReact<AppRouter>();
