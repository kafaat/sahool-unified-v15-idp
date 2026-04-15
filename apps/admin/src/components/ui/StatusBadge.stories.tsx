import type { Meta, StoryObj } from '@storybook/react';
import { StatusBadge } from './StatusBadge';

const meta: Meta<typeof StatusBadge> = {
  title: 'UI/StatusBadge',
  component: StatusBadge,
  tags: ['autodocs'],
  argTypes: {
    status: {
      control: 'select',
      options: ['active', 'inactive', 'pending', 'completed', 'error'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
    locale: {
      control: 'select',
      options: ['ar', 'en'],
    },
  },
};
export default meta;

type Story = StoryObj<typeof StatusBadge>;

export const Active: Story = {
  args: { status: 'active', locale: 'ar', size: 'md' },
};

export const Inactive: Story = {
  args: { status: 'inactive', locale: 'ar', size: 'md' },
};

export const Pending: Story = {
  args: { status: 'pending', locale: 'ar', size: 'md' },
};

export const Completed: Story = {
  args: { status: 'completed', locale: 'ar', size: 'md' },
};

export const Error: Story = {
  args: { status: 'error', locale: 'ar', size: 'md' },
};

export const AllSizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <StatusBadge status="active" size="sm" />
      <StatusBadge status="active" size="md" />
      <StatusBadge status="active" size="lg" />
    </div>
  ),
};

export const English: Story = {
  args: { status: 'active', locale: 'en', size: 'md' },
};
