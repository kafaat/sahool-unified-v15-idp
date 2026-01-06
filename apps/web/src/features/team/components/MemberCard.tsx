'use client';

/**
 * SAHOOL Member Card Component
 * مكون بطاقة العضو
 */

import React from 'react';
import { Mail, Phone, Clock, MoreVertical, Edit, Trash2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { TeamMember, ROLE_CONFIGS } from '../types/team';

interface MemberCardProps {
  member: TeamMember;
  onEditRole?: (member: TeamMember) => void;
  onRemove?: (member: TeamMember) => void;
}

export const MemberCard: React.FC<MemberCardProps> = ({
  member,
  onEditRole,
  onRemove,
}) => {
  const [showActions, setShowActions] = React.useState(false);
  const roleConfig = ROLE_CONFIGS[member.role];

  const formatLastActive = (date?: string) => {
    if (!date) return 'لم يسجل دخول بعد';

    const now = new Date();
    const lastActive = new Date(date);
    const diffMinutes = Math.floor((now.getTime() - lastActive.getTime()) / (1000 * 60));

    if (diffMinutes < 60) {
      return `منذ ${diffMinutes} دقيقة`;
    }
    if (diffMinutes < 1440) {
      const hours = Math.floor(diffMinutes / 60);
      return `منذ ${hours} ساعة`;
    }
    const days = Math.floor(diffMinutes / 1440);
    return `منذ ${days} يوم`;
  };

  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 p-4 hover:border-blue-300 transition-colors relative">
      {/* Actions Menu */}
      {(onEditRole || onRemove) && (
        <div className="absolute top-4 right-4">
          <button
            onClick={() => setShowActions(!showActions)}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <MoreVertical className="w-5 h-5 text-gray-500" />
          </button>

          {showActions && (
            <div className="absolute top-8 right-0 bg-white border-2 border-gray-200 rounded-lg shadow-lg z-10 min-w-[160px]">
              {onEditRole && (
                <button
                  onClick={() => {
                    onEditRole(member);
                    setShowActions(false);
                  }}
                  className="w-full flex items-center gap-2 px-4 py-2 hover:bg-gray-50 text-right"
                >
                  <Edit className="w-4 h-4" />
                  <span>تعديل الدور</span>
                </button>
              )}
              {onRemove && (
                <button
                  onClick={() => {
                    onRemove(member);
                    setShowActions(false);
                  }}
                  className="w-full flex items-center gap-2 px-4 py-2 hover:bg-red-50 text-red-600 text-right"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>إزالة</span>
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Avatar */}
      <div className="flex items-start gap-4 mb-4">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
          {member.avatarUrl ? (
            <img
              src={member.avatarUrl}
              alt={`${member.firstName} ${member.lastName}`}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            <span>{member.firstName[0]}{member.lastName[0]}</span>
          )}
        </div>

        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900 mb-1">
            {member.firstName} {member.lastName}
          </h3>
          <Badge className={roleConfig.color} size="sm">
            {roleConfig.nameAr}
          </Badge>
        </div>
      </div>

      {/* Contact Info */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-gray-600">
          <Mail className="w-4 h-4" />
          <span className="text-sm">{member.email}</span>
        </div>

        {member.phone && (
          <div className="flex items-center gap-2 text-gray-600">
            <Phone className="w-4 h-4" />
            <span className="text-sm">{member.phone}</span>
          </div>
        )}
      </div>

      {/* Status & Last Active */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-200">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-gray-400" />
          <span className="text-xs text-gray-500">
            {formatLastActive(member.lastLoginAt)}
          </span>
        </div>

        <Badge
          variant={member.status === 'ACTIVE' ? 'success' : member.status === 'PENDING' ? 'warning' : 'default'}
          size="sm"
        >
          {member.status === 'ACTIVE' ? 'نشط' : member.status === 'PENDING' ? 'قيد الانتظار' : 'غير نشط'}
        </Badge>
      </div>
    </div>
  );
};

export default MemberCard;
