/**
 * Custom Decorators for Chat Service Authentication
 * مزخرفات مخصصة للمصادقة
 */

import { createParamDecorator, ExecutionContext } from "@nestjs/common";

/**
 * Current User decorator
 *
 * Extract the current authenticated user from the request
 *
 * @example
 * ```typescript
 * @Get()
 * getProfile(@CurrentUser() user: any) {
 *   return { userId: user.id };
 * }
 *
 * // Get specific property
 * @Get('email')
 * getEmail(@CurrentUser('email') email: string) {
 *   return { email };
 * }
 * ```
 */
export const CurrentUser = createParamDecorator(
  (data: string | undefined, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    const user = request.user;

    return data ? user?.[data] : user;
  },
);

/**
 * User ID decorator
 *
 * Extract the user ID from the authenticated user
 *
 * @example
 * ```typescript
 * @Get('conversations')
 * getUserConversations(@UserId() userId: string) {
 *   return this.chatService.getUserConversations(userId);
 * }
 * ```
 */
export const UserId = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string => {
    const request = ctx.switchToHttp().getRequest();
    return request.user?.id;
  },
);
