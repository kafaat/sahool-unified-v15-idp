import * as React from 'react';
import { clsx } from 'clsx';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'bordered' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  /** Make the card interactive (focusable, hoverable) */
  interactive?: boolean;
  /** Card as a link wrapper */
  as?: 'div' | 'article' | 'section';
  ref?: React.Ref<HTMLDivElement>;
}

export function Card({
  className,
  variant = 'default',
  padding = 'md',
  interactive = false,
  as: Component = 'div',
  children,
  ref,
  role,
  tabIndex,
  ...props
}: CardProps) {
  const variants = {
    default: 'bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700',
    bordered: 'bg-white dark:bg-slate-800 border-2 border-sahool-green-200 dark:border-green-800',
    elevated: 'bg-white dark:bg-slate-800 shadow-lg dark:shadow-slate-900/50 border border-gray-100 dark:border-slate-700',
  };

  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const interactiveStyles = interactive
    ? 'cursor-pointer hover:shadow-md dark:hover:shadow-slate-900/50 transition-shadow focus:outline-none focus:ring-2 focus:ring-sahool-green-500 dark:focus:ring-green-400 focus:ring-offset-2 dark:focus:ring-offset-slate-800'
    : '';

  return (
    <Component
      ref={ref}
      className={clsx(
        'rounded-lg',
        variants[variant],
        paddings[padding],
        interactiveStyles,
        className
      )}
      role={role || (interactive ? 'button' : undefined)}
      tabIndex={tabIndex ?? (interactive ? 0 : undefined)}
      {...props}
    >
      {children}
    </Component>
  );
}

Card.displayName = 'Card';

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  ref?: React.Ref<HTMLDivElement>;
}

export function CardHeader({ className, ref, ...props }: CardHeaderProps) {
  return <div ref={ref} className={clsx('mb-4', className)} {...props} />;
}

CardHeader.displayName = 'CardHeader';

export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  ref?: React.Ref<HTMLHeadingElement>;
}

export function CardTitle({ className, ref, ...props }: CardTitleProps) {
  return <h3 ref={ref} className={clsx('text-xl font-bold text-gray-900 dark:text-slate-100', className)} {...props} />;
}

CardTitle.displayName = 'CardTitle';

export interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  ref?: React.Ref<HTMLParagraphElement>;
}

export function CardDescription({ className, ref, ...props }: CardDescriptionProps) {
  return <p ref={ref} className={clsx('text-sm text-gray-600 dark:text-slate-400 mt-1', className)} {...props} />;
}

CardDescription.displayName = 'CardDescription';

export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  ref?: React.Ref<HTMLDivElement>;
}

export function CardContent({ className, ref, ...props }: CardContentProps) {
  return <div ref={ref} className={clsx('', className)} {...props} />;
}

CardContent.displayName = 'CardContent';

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  ref?: React.Ref<HTMLDivElement>;
}

export function CardFooter({ className, ref, ...props }: CardFooterProps) {
  return (
    <div ref={ref} className={clsx('mt-4 pt-4 border-t border-gray-200 dark:border-slate-700', className)} {...props} />
  );
}

CardFooter.displayName = 'CardFooter';
