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
    default: 'bg-white border border-gray-200',
    bordered: 'bg-white border-2 border-sahool-green-200',
    elevated: 'bg-white shadow-lg border border-gray-100',
  };

  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const interactiveStyles = interactive
    ? 'cursor-pointer hover:shadow-md transition-shadow focus:outline-none focus:ring-2 focus:ring-sahool-green-500 focus:ring-offset-2'
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
  return <h3 ref={ref} className={clsx('text-xl font-bold text-gray-900', className)} {...props} />;
}

CardTitle.displayName = 'CardTitle';

export interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  ref?: React.Ref<HTMLParagraphElement>;
}

export function CardDescription({ className, ref, ...props }: CardDescriptionProps) {
  return <p ref={ref} className={clsx('text-sm text-gray-600 mt-1', className)} {...props} />;
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
    <div ref={ref} className={clsx('mt-4 pt-4 border-t border-gray-200', className)} {...props} />
  );
}

CardFooter.displayName = 'CardFooter';
