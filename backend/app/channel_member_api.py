"""
頻道成員管理 API
處理頻道成員的加入、離開、角色管理和擁有權轉移
"""
from flask import request, jsonify, g
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import expose
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt

from .auth import jwt_required
from .models import ChannelMember, ChatChannel
from . import db

bcrypt = Bcrypt()


class ChannelMemberApi(ModelRestApi):
    """頻道成員管理 API"""
    datamodel = SQLAInterface(ChannelMember)
    
    # 🔒 安全性：禁用不必要的端點
    base_permissions = []
    
    @expose('/channel/<int:channel_id>/members')
    @jwt_required
    def get_channel_members(self, channel_id):
        """獲取頻道成員列表"""
        try:
            # 檢查用戶是否有權限查看頻道成員
            current_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=g.user.id,
                status='active'
            ).first()
            
            if not current_member:
                return jsonify({'error': '您不是此頻道的成員'}), 403
            
            # 獲取頻道所有 active 成員
            members = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                status='active'
            ).order_by(ChannelMember.role.desc(), ChannelMember.created_on.asc()).all()
            
            return jsonify({
                'result': [member.to_dict() for member in members]
            })
            
        except Exception as e:
            return jsonify({'error': f'獲取成員列表失敗: {str(e)}'}), 500

    @expose('/join-by-id', methods=['POST'])
    @jwt_required
    def join_channel_by_id(self):
        """通過頻道ID和密碼加入頻道"""
        try:
            data = request.get_json()
            channel_id = data.get('channel_id')
            password = data.get('password', '')
            
            if not channel_id:
                return jsonify({'error': '頻道ID不能為空'}), 400

            # 驗證頻道和密碼
            channel = db.session.query(ChatChannel).filter_by(
                id=channel_id,
                is_active=True,
                allow_join_by_id=True
            ).first()

            if not channel:
                return jsonify({'error': '頻道不存在或不允許加入'}), 404

            # 檢查密碼
            if channel.password_required:
                if not password:
                    return jsonify({'error': '此頻道需要密碼'}), 401
                if not bcrypt.check_password_hash(channel.join_password, password):
                    return jsonify({'error': '密碼錯誤'}), 401

            # 🛡️ 防重入：檢查是否已經是 active 成員
            existing_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=g.user.id,
                status='active'
            ).first()

            if existing_member:
                return jsonify({'error': '您已經是此頻道的成員'}), 400

            # 檢查是否有 left 狀態的記錄，若有則更新為 active
            pending_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=g.user.id
            ).filter(ChannelMember.status.in_(['invited', 'left'])).first()

            if pending_member:
                # 重新激活現有記錄
                pending_member.status = 'active'
                pending_member.changed_on = datetime.now(timezone.utc)
                pending_member.changed_by_fk = g.user.id
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': '成功重新加入頻道',
                    'data': {
                        'channel': channel.to_dict(),
                        'member': pending_member.to_dict()
                    }
                })

            # 檢查頻道成員數量限制
            if channel.member_count >= channel.max_members:
                return jsonify({'error': f'頻道已滿（最大 {channel.max_members} 人）'}), 400

            # 加入頻道
            member = ChannelMember(
                channel_id=channel_id,
                user_id=g.user.id,
                role='member',
                status='active',
                created_by_fk=g.user.id,
                changed_by_fk=g.user.id
            )
            db.session.add(member)
            db.session.commit()

            # 成員數量會通過 Hook 自動更新

            return jsonify({
                'success': True,
                'message': '成功加入頻道',
                'data': {
                    'channel': channel.to_dict(),
                    'member': member.to_dict()
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'加入頻道失敗: {str(e)}'}), 500

    @expose('/channel/<int:channel_id>/leave', methods=['POST'])
    @jwt_required
    def leave_channel(self, channel_id):
        """離開頻道"""
        try:
            member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=g.user.id,
                status='active'
            ).first()

            if not member:
                return jsonify({'error': '您不是此頻道的成員'}), 400

            # 🛡️ Owner 風險控制：檢查是否需要轉移擁有權
            if member.role == 'owner':
                # 檢查頻道是否還有其他 active 成員
                other_members = db.session.query(ChannelMember).filter_by(
                    channel_id=channel_id,
                    status='active'
                ).filter(ChannelMember.user_id != g.user.id).all()

                if other_members:
                    # 有其他成員，需要轉移擁有權
                    return jsonify({
                        'error': '頻道創建者需要先轉移擁有權才能離開',
                        'transfer_required': True,
                        'available_members': [
                            {
                                'user_id': m.user_id,
                                'username': m.user.username,
                                'display_name': getattr(m.user.profile, 'display_name', m.user.username) if hasattr(m.user, 'profile') and m.user.profile else m.user.username,
                                'role': m.role
                            } for m in other_members
                        ]
                    }), 400

            # 更新成員狀態為離開
            member.status = 'left'
            member.changed_on = datetime.now(timezone.utc)
            member.changed_by_fk = g.user.id
            db.session.commit()

            # 成員數量會通過 Hook 自動更新

            return jsonify({'success': True, 'message': '成功離開頻道'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'離開頻道失敗: {str(e)}'}), 500

    @expose('/channel/<int:channel_id>/remove/<int:user_id>', methods=['POST'])
    @jwt_required
    def remove_member(self, channel_id, user_id):
        """移除頻道成員"""
        try:
            # 權限檢查
            current_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=g.user.id,
                status='active'
            ).first()

            if not current_member or current_member.role not in ['owner', 'admin']:
                return jsonify({'error': '權限不足'}), 403

            # 找到要移除的成員
            target_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=user_id,
                status='active'
            ).first()

            if not target_member:
                return jsonify({'error': '成員不存在'}), 404

            if target_member.role == 'owner':
                return jsonify({'error': '無法移除頻道創建者'}), 403

            # 只有 owner 可以移除 admin
            if target_member.role == 'admin' and current_member.role != 'owner':
                return jsonify({'error': '只有頻道創建者可以移除管理員'}), 403

            # 移除成員（設為 banned 狀態）
            target_member.status = 'banned'
            target_member.changed_on = datetime.now(timezone.utc)
            target_member.changed_by_fk = g.user.id
            db.session.commit()

            # 成員數量會通過 Hook 自動更新

            return jsonify({'success': True, 'message': '成功移除成員'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'移除成員失敗: {str(e)}'}), 500

    @expose('/channel/<int:channel_id>/transfer-ownership/<int:new_owner_id>', methods=['POST'])
    @jwt_required
    def transfer_ownership(self, channel_id, new_owner_id):
        """🔄 轉移頻道擁有權"""
        try:
            # 檢查當前用戶是否為 Owner
            current_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=g.user.id,
                status='active',
                role='owner'
            ).first()

            if not current_member:
                return jsonify({'error': '只有頻道創建者可以轉移擁有權'}), 403

            # 檢查新 Owner 是否為有效成員
            new_owner_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=new_owner_id,
                status='active'
            ).first()

            if not new_owner_member:
                return jsonify({'error': '目標用戶不是此頻道的成員'}), 404

            if new_owner_member.user_id == g.user.id:
                return jsonify({'error': '不能轉移給自己'}), 400

            # 執行轉移
            # 原 Owner 變成 Admin
            current_member.role = 'admin'
            current_member.changed_on = datetime.now(timezone.utc)
            current_member.changed_by_fk = g.user.id

            # 新成員變成 Owner
            new_owner_member.role = 'owner'
            new_owner_member.changed_on = datetime.now(timezone.utc)
            new_owner_member.changed_by_fk = g.user.id

            # 更新頻道的 creator_id
            channel = db.session.query(ChatChannel).filter_by(id=channel_id).first()
            if channel:
                channel.creator_id = new_owner_id
                channel.changed_on = datetime.now(timezone.utc)
                channel.changed_by_fk = g.user.id

            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'成功轉移頻道擁有權給 {new_owner_member.user.username}',
                'data': {
                    'new_owner': new_owner_member.to_dict(),
                    'former_owner': current_member.to_dict()
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'轉移失敗: {str(e)}'}), 500

    @expose('/channel/<int:channel_id>/role/<int:user_id>', methods=['PUT'])
    @jwt_required
    def update_member_role(self, channel_id, user_id):
        """更新成員角色"""
        try:
            data = request.get_json()
            new_role = data.get('role')
            
            if new_role not in ['member', 'admin']:
                return jsonify({'error': '無效的角色'}), 400

            # 權限檢查：只有 Owner 可以更改角色
            current_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=g.user.id,
                status='active',
                role='owner'
            ).first()

            if not current_member:
                return jsonify({'error': '只有頻道創建者可以更改成員角色'}), 403

            # 找到目標成員
            target_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=user_id,
                status='active'
            ).first()

            if not target_member:
                return jsonify({'error': '成員不存在'}), 404

            if target_member.role == 'owner':
                return jsonify({'error': '無法更改創建者角色'}), 403

            # 更新角色
            old_role = target_member.role
            target_member.role = new_role
            target_member.changed_on = datetime.now(timezone.utc)
            target_member.changed_by_fk = g.user.id
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'成功將 {target_member.user.username} 的角色從 {old_role} 更改為 {new_role}',
                'data': target_member.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'更新角色失敗: {str(e)}'}), 500

    @expose('/channel/<int:channel_id>/reset-password', methods=['POST'])
    @jwt_required
    def reset_channel_password(self, channel_id):
        """重置頻道密碼（僅限 owner/admin）"""
        try:
            data = request.get_json()
            new_password = data.get('new_password')
            
            if not new_password or len(new_password) < 6:
                return jsonify({'error': '新密碼長度至少6位字符'}), 400

            # 權限檢查：只有 owner 和 admin 可以重置密碼
            current_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=g.user.id,
                status='active'
            ).first()

            if not current_member or current_member.role not in ['owner', 'admin']:
                return jsonify({'error': '只有頻道創建者和管理員可以重置密碼'}), 403

            # 檢查頻道是否存在
            channel = db.session.query(ChatChannel).filter_by(
                id=channel_id,
                is_active=True
            ).first()

            if not channel:
                return jsonify({'error': '頻道不存在'}), 404

            # 更新密碼
            channel.join_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            channel.password_required = True
            channel.changed_on = datetime.now(timezone.utc)
            channel.changed_by_fk = g.user.id
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '頻道密碼已重置',
                'data': {
                    'new_password': new_password,  # 返回明文密碼供管理員記錄
                    'channel_id': channel_id
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'重置密碼失敗: {str(e)}'}), 500

    @expose('/channel/<int:channel_id>/info', methods=['GET'])
    @jwt_required
    def get_channel_admin_info(self, channel_id):
        """獲取頻道管理資訊（僅限 owner/admin）"""
        try:
            # 權限檢查：只有 owner 和 admin 可以查看管理資訊
            current_member = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                user_id=g.user.id,
                status='active'
            ).first()

            if not current_member or current_member.role not in ['owner', 'admin']:
                return jsonify({'error': '只有頻道創建者和管理員可以查看此資訊'}), 403

            # 獲取頻道資訊
            channel = db.session.query(ChatChannel).filter_by(
                id=channel_id,
                is_active=True
            ).first()

            if not channel:
                return jsonify({'error': '頻道不存在'}), 404

            # 獲取所有管理員列表
            admins_and_owner = db.session.query(ChannelMember).filter_by(
                channel_id=channel_id,
                status='active'
            ).filter(ChannelMember.role.in_(['owner', 'admin'])).all()

            return jsonify({
                'success': True,
                'data': {
                    'channel': {
                        'id': channel.id,
                        'name': channel.name,
                        'description': channel.description,
                        'is_private': channel.is_private,
                        'allow_join_by_id': channel.allow_join_by_id,
                        'password_required': channel.password_required,
                        'member_count': channel.member_count,
                        'max_members': channel.max_members,
                        'creator_id': channel.creator_id,
                        'created_on': channel.created_on.isoformat() if channel.created_on else None
                    },
                    'admins': [
                        {
                            'user_id': member.user_id,
                            'username': member.user.username,
                            'display_name': getattr(member.user.profile, 'display_name', member.user.username) if hasattr(member.user, 'profile') and member.user.profile else member.user.username,
                            'role': member.role,
                            'joined_on': member.created_on.isoformat() if member.created_on else None
                        } for member in admins_and_owner
                    ],
                    'password_status': {
                        'has_password': bool(channel.join_password),
                        'can_reset_password': current_member.role in ['owner', 'admin']
                    }
                }
            })
            
        except Exception as e:
            return jsonify({'error': f'獲取頻道資訊失敗: {str(e)}'}), 500