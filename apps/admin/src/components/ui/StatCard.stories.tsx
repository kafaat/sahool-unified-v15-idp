import type { Meta, StoryObj } from '@storybook/react';
import StatCard from './StatCard';
import { Leaf, Droplets, Activity, AlertTriangle } from 'lucide-react';

const meta: Meta<typeof StatCard> = {
  title: 'UI/StatCard',
  component: StatCard,
  tags: ['autodocs'],
  argTypes: {
    iconColor: {
      control: 'select',
      options: ['text-green-600', 'text-blue-600', 'text-red-600', 'text-sahool-600'],
    },
  },
};
export default meta;

type Story = StoryObj<typeof StatCard>;

export const Default: Story = {
  args: {
    title: 'إجمالي الحقول',
    value: 245,
    icon: Leaf,
    iconColor: 'text-green-600',
  },
};

export const WithTrendUp: Story = {
  args: {
    title: 'متوسط NDVI',
    value: '0.72',
    icon: Activity,
    iconColor: 'text-sahool-600',
    trend: { value: 12, isPositive: true },
  },
};

export const WithTrendDown: Story = {
  args: {
    title: 'حالات حرجة',
    value: 8,
    icon: AlertTriangle,
    iconColor: 'text-red-600',
    trend: { value: 5, isPositive: false },
  },
};

export const WithSuffix: Story = {
  args: {
    title: 'استهلاك المياه',
    value: 2450,
    icon: Droplets,
    iconColor: 'text-blue-600',
    suffix: 'م³',
  },
};
