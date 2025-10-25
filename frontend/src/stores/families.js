import { defineStore } from 'pinia'
import { api } from 'boot/axios'

export const useFamilyStore = defineStore('families', {
  state: () => ({
    families: [],
    currentFamily: null,
    familyMembers: [],
    invitations: [],
    loading: false,
    error: null
  }),

  getters: {
    // Get current user's role in current family
    currentUserRole: (state) => {
      if (!state.currentFamily || !state.familyMembers.length) {
        console.log('FamilyStore: currentUserRole - no family or members', {
          currentFamily: state.currentFamily,
          familyMembersLength: state.familyMembers.length
        })
        return null
      }

      const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
      const member = state.familyMembers.find(m => m.user?.id === currentUser.id)

      console.log('FamilyStore: currentUserRole check:', {
        currentUserId: currentUser.id,
        familyMembers: state.familyMembers,
        foundMember: member,
        role: member?.role
      })

      return member?.role || null
    },

    // Check if current user is admin
    isCurrentUserAdmin() {
      return this.currentUserRole === 'admin'
    },

    // Check if current user is a child
    isCurrentUserChild: (state) => {
      return state.currentUserRole === 'child'
    },

    // Check if current user has specific permission
    hasPermission: (state) => (permission) => {
      if (!state.currentFamily || !state.familyMembers.length) return false

      const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
      const member = state.familyMembers.find(m => m.user.id === currentUser.id)

      if (!member) return false
      if (member.role === 'admin') return true

      const permissionMap = {
        'create_meal_plans': member.can_create_meal_plans,
        'manage_recipes': member.can_manage_recipes,
        'manage_shopping_lists': member.can_manage_shopping_lists,
        'invite_members': member.can_invite_members
      }

      return permissionMap[permission] || false
    },

    // Get pending invitations count
    pendingInvitationsCount: (state) => {
      return state.invitations.filter(inv => inv.status === 'pending').length
    }
  },

  actions: {
    // Fetch all families for current user
    async fetchFamilies() {
      console.log('FamilyStore: Fetching families...')
      this.loading = true
      this.error = null

      try {
        const response = await api.get('/families/')
        console.log('FamilyStore: Families response:', response.data)
        this.families = response.data.results || response.data
        console.log('FamilyStore: Families set:', this.families.length, 'families')

        // Set first family as current if none selected
        if (this.families.length > 0 && !this.currentFamily) {
          console.log('FamilyStore: Setting first family as current')
          await this.setCurrentFamily(this.families[0].id)
        }
      } catch (error) {
        console.error('FamilyStore: Error fetching families:', error)
        console.error('FamilyStore: Error response:', error.response?.data)
        this.error = error.response?.data?.detail || 'Failed to fetch families'
      } finally {
        this.loading = false
      }
    },

    // Set current family and fetch its members
    async setCurrentFamily(familyId) {
      try {
        const family = this.families.find(f => f.id === familyId)
        if (family) {
          this.currentFamily = family
          localStorage.setItem('currentFamilyId', familyId)
          await this.fetchFamilyMembers(familyId)
        }
      } catch (error) {
        console.error('Error setting current family:', error)
        this.error = error.response?.data?.detail || 'Failed to set current family'
      }
    },

    // Fetch family members
    async fetchFamilyMembers(familyId = null) {
      const id = familyId || this.currentFamily?.id
      if (!id) return

      try {
        const response = await api.get(`/families/${id}/members/`)
        this.familyMembers = response.data

        // Save to localStorage for navigation access
        localStorage.setItem('familyMembers', JSON.stringify(this.familyMembers))
      } catch (error) {
        console.error('Error fetching family members:', error)
        this.error = error.response?.data?.detail || 'Failed to fetch family members'
      }
    },

    // Create new family
    async createFamily(familyData) {
      this.loading = true
      this.error = null

      try {
        const response = await api.post('/families/', familyData)
        const newFamily = response.data

        this.families.push(newFamily)
        await this.setCurrentFamily(newFamily.id)

        return newFamily
      } catch (error) {
        console.error('Error creating family:', error)
        this.error = error.response?.data?.detail || 'Failed to create family'
        throw error
      } finally {
        this.loading = false
      }
    },

    // Update family
    async updateFamily(familyId, familyData) {
      try {
        const response = await api.patch(`/families/${familyId}/`, familyData)
        const updatedFamily = response.data

        // Update in families list
        const index = this.families.findIndex(f => f.id === familyId)
        if (index !== -1) {
          this.families[index] = updatedFamily
        }

        // Update current family if it's the one being updated
        if (this.currentFamily?.id === familyId) {
          this.currentFamily = updatedFamily
        }

        return updatedFamily
      } catch (error) {
        console.error('Error updating family:', error)
        this.error = error.response?.data?.detail || 'Failed to update family'
        throw error
      }
    },

    // Invite family member
    async inviteMember(familyId, invitationData) {
      try {
        const response = await api.post(`/families/${familyId}/invite_member/`, invitationData)
        return response.data
      } catch (error) {
        console.error('Error inviting member:', error)
        this.error = error.response?.data?.detail || 'Failed to invite member'
        throw error
      }
    },

    // Update family member
    async updateMember(familyId, memberData) {
      try {
        const response = await api.patch(`/families/${familyId}/update_member/`, memberData)

        // Update in local state
        const index = this.familyMembers.findIndex(m => m.id === memberData.member_id)
        if (index !== -1) {
          this.familyMembers[index] = response.data
        }

        return response.data
      } catch (error) {
        console.error('Error updating member:', error)
        this.error = error.response?.data?.detail || 'Failed to update member'
        throw error
      }
    },

    // Remove family member (legacy method - use removeMember instead)
    async removeFamilyMember(familyId, memberId) {
      try {
        await api.delete(`/families/${familyId}/remove_member/`, {
          data: { member_id: memberId }
        })

        // Remove from local state
        this.familyMembers = this.familyMembers.filter(m => m.id !== memberId)
      } catch (error) {
        console.error('Error removing member:', error)
        this.error = error.response?.data?.detail || 'Failed to remove member'
        throw error
      }
    },

    // Fetch pending invitations
    async fetchInvitations() {
      try {
        const response = await api.get('/families/invitations/')
        this.invitations = response.data
      } catch (error) {
        console.error('Error fetching invitations:', error)
        this.error = error.response?.data?.detail || 'Failed to fetch invitations'
      }
    },

    // Accept invitation
    async acceptInvitation(invitationId) {
      try {
        await api.post('/families/accept_invitation/', {
          invitation_id: invitationId
        })

        // Remove from invitations and refresh families
        this.invitations = this.invitations.filter(inv => inv.id !== invitationId)
        await this.fetchFamilies()
      } catch (error) {
        console.error('Error accepting invitation:', error)
        this.error = error.response?.data?.detail || 'Failed to accept invitation'
        throw error
      }
    },

    // Decline invitation
    async declineInvitation(invitationId) {
      try {
        await api.post('/families/decline_invitation/', {
          invitation_id: invitationId
        })

        // Remove from invitations
        this.invitations = this.invitations.filter(inv => inv.id !== invitationId)
      } catch (error) {
        console.error('Error declining invitation:', error)
        this.error = error.response?.data?.detail || 'Failed to decline invitation'
        throw error
      }
    },

    // Initialize family context (call on app startup)
    async initializeFamilyContext() {
      await this.fetchFamilies()
      await this.fetchInvitations()

      // Restore current family from localStorage
      const savedFamilyId = localStorage.getItem('currentFamilyId')
      if (savedFamilyId && this.families.some(f => f.id === savedFamilyId)) {
        await this.setCurrentFamily(savedFamilyId)
      }
    },

    // Create family member (direct user creation)
    async createMember(memberData) {
      try {
        const response = await api.post('families/create_member/', memberData)

        // Refresh family members after creation
        if (this.currentFamily) {
          await this.fetchFamilyMembers(this.currentFamily.id)
        }

        return response.data
      } catch (error) {
        console.error('Error creating family member:', error)
        this.error = error.response?.data?.error || 'Failed to create family member'
        throw error
      }
    },

    // Update member role (simplified method)
    async updateMemberRole(memberId, newRole) {
      if (!this.currentFamily) {
        throw new Error('No current family selected')
      }

      try {
        const response = await api.patch(`/families/${this.currentFamily.id}/update_member/`, {
          member_id: memberId,
          role: newRole
        })

        // Update in local state
        const index = this.familyMembers.findIndex(m => m.id === memberId)
        if (index !== -1) {
          this.familyMembers[index] = response.data
        }

        return response.data
      } catch (error) {
        console.error('Error updating member role:', error)
        this.error = error.response?.data?.error || 'Failed to update member role'
        throw error
      }
    },

    // Remove member (simplified method)
    async removeMember(memberId) {
      if (!this.currentFamily) {
        throw new Error('No current family selected')
      }

      try {
        await api.delete(`/families/${this.currentFamily.id}/remove_member/`, {
          data: { member_id: memberId }
        })

        // Remove from local state
        this.familyMembers = this.familyMembers.filter(m => m.id !== memberId)
      } catch (error) {
        console.error('Error removing member:', error)
        this.error = error.response?.data?.error || 'Failed to remove member'
        throw error
      }
    },

    // Get family activity feed
    async fetchFamilyActivity(familyId = null) {
      const id = familyId || this.currentFamily?.id
      if (!id) return []

      try {
        // Mock activity data for now
        // In real implementation, this would fetch from API
        return [
          {
            id: 1,
            type: 'recipe_created',
            user: 'John Doe',
            title: 'New recipe added',
            description: 'Spaghetti Carbonara',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
            icon: 'restaurant_menu',
            color: 'primary'
          },
          {
            id: 2,
            type: 'meal_plan_created',
            user: 'Sarah Smith',
            title: 'Meal plan created',
            description: 'Week of January 8-14',
            timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
            icon: 'calendar_today',
            color: 'secondary'
          }
        ]
      } catch (error) {
        console.error('Error fetching family activity:', error)
        return []
      }
    },

    // Get family statistics
    async getFamilyStats(familyId = null) {
      const id = familyId || this.currentFamily?.id
      if (!id) return {}

      try {
        // Mock stats for now
        return {
          totalRecipes: 25,
          totalMealPlans: 8,
          totalShoppingLists: 12,
          activeMembers: this.familyMembers.length,
          thisWeekMeals: 21,
          completedShoppingLists: 8
        }
      } catch (error) {
        console.error('Error fetching family stats:', error)
        return {}
      }
    },

    // Send family invitation via email
    async sendFamilyInvitation(email, role = 'member', message = '') {
      if (!this.currentFamily) {
        throw new Error('No current family selected')
      }

      try {
        const response = await api.post(`/families/${this.currentFamily.id}/invite_member/`, {
          email,
          role,
          message
        })

        return response.data
      } catch (error) {
        console.error('Error sending family invitation:', error)
        this.error = error.response?.data?.error || 'Failed to send invitation'
        throw error
      }
    },

    // Clear family data (on logout)
    clearFamilyData() {
      this.families = []
      this.currentFamily = null
      this.familyMembers = []
      this.invitations = []
      this.loading = false
      this.error = null
      localStorage.removeItem('currentFamilyId')
      localStorage.removeItem('familyMembers')
    }
  }
})
