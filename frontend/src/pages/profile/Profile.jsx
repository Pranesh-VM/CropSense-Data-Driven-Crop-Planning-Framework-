import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useQuery } from '@tanstack/react-query';
import { authService } from '../../services/api';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';

export const Profile = () => {
  const { logout } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  
  // Fetch profile data from backend
  const { data: profileData, isLoading, error } = useQuery({
    queryKey: ['profile'],
    queryFn: authService.getProfile,
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 2,
  });

  const profile = profileData?.profile;

  const { register, handleSubmit, formState: { errors }, reset } = useForm({
    defaultValues: {
      username: '',
      email: '',
      phone: '',
    },
  });

  React.useEffect(() => {
    if (profile) {
      reset({
        username: profile.username || '',
        email: profile.email || '',
        phone: profile.phone || '',
      });
    }
  }, [profile, reset]);

  const onSubmit = (data) => {
    // Profile update would be implemented when backend supports it
    toast.success('Profile changes saved! (This is a demo - not yet saved to backend)');
    setIsEditing(false);
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully!');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 md:p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
            <p className="text-red-900 text-lg font-semibold">Failed to load profile</p>
            <p className="text-red-700 mt-2">Please try refreshing the page</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">👤 Profile</h1>
          <p className="text-gray-600 mt-2">Manage your account settings</p>
        </div>

        {/* Profile Card */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          {/* Avatar & Basic Info */}
          <div className="flex flex-col md:flex-row items-center gap-6 pb-6 border-b border-gray-200">
            <div className="w-24 h-24 bg-gradient-to-br from-emerald-400 to-blue-500 rounded-full flex items-center justify-center text-white text-5xl font-bold">
              {profile?.username?.charAt(0).toUpperCase() || 'U'}
            </div>

            <div className="flex-1 text-center md:text-left">
              <h2 className="text-3xl font-bold text-gray-900 capitalize">
                {profile?.username || 'User'}
              </h2>
              <p className="text-gray-600 mt-1">{profile?.email || 'No email'}</p>
              <div className="mt-3 flex gap-2 justify-center md:justify-start">
                <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-semibold">
                  Active Farmer
                </span>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                  ID: {profile?.farmer_id}
                </span>
              </div>
            </div>

            <button
              onClick={() => setIsEditing(!isEditing)}
              className="px-6 py-2 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-lg transition"
            >
              {isEditing ? 'Cancel' : 'Edit'}
            </button>
          </div>

          {/* Account Information */}
          <div className="mt-8">
            {isEditing ? (
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Edit Information</h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.username ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('username', { required: 'Username is required' })}
                  />
                  {errors.username && (
                    <p className="text-red-500 text-xs mt-1">{errors.username.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.email ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('email', {
                      required: 'Email is required',
                      pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Invalid email' },
                    })}
                  />
                  {errors.email && (
                    <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.phone ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('phone', {
                      pattern: { value: /^[0-9]{10}$/, message: 'Phone must be 10 digits' },
                    })}
                  />
                  {errors.phone && (
                    <p className="text-red-500 text-xs mt-1">{errors.phone.message}</p>
                  )}
                </div>

                <button
                  type="submit"
                  className="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-2 px-4 rounded-lg transition"
                >
                  Save Changes
                </button>
              </form>
            ) : (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <p className="text-gray-600 text-sm mb-1">👤 Username</p>
                    <p className="text-lg font-semibold text-gray-900 capitalize">
                      {profile?.username || 'N/A'}
                    </p>
                  </div>

                  <div>
                    <p className="text-gray-600 text-sm mb-1">📧 Email</p>
                    <p className="text-lg font-semibold text-gray-900">{profile?.email || 'N/A'}</p>
                  </div>

                  <div>
                    <p className="text-gray-600 text-sm mb-1">📱 Phone</p>
                    <p className="text-lg font-semibold text-gray-900">{profile?.phone || 'Not provided'}</p>
                  </div>

                  <div>
                    <p className="text-gray-600 text-sm mb-1">🆔 Farmer ID</p>
                    <p className="text-lg font-semibold text-gray-900">
                      #{profile?.farmer_id || 'N/A'}
                    </p>
                  </div>

                  <div>
                    <p className="text-gray-600 text-sm mb-1">📅 Member Since</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {profile?.created_at
                        ? new Date(profile.created_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })
                        : 'N/A'}
                    </p>
                  </div>

                  <div>
                    <p className="text-gray-600 text-sm mb-1">🕐 Last Login</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {profile?.last_login
                        ? new Date(profile.last_login).toLocaleString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })
                        : 'N/A'}
                    </p>
                  </div>
                </div>

                {profile?.last_login && (
                  <div className="mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                    <p className="text-emerald-900 text-sm flex items-center gap-2">
                      <span className="text-lg">✓</span>
                      <span>
                        <strong>Active Account:</strong> Last accessed on {new Date(profile.last_login).toLocaleDateString('en-US', { 
                          weekday: 'long',
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Account Settings */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Account Settings</h2>

          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 border border-gray-200 rounded-lg">
              <div>
                <p className="font-semibold text-gray-900">Email Notifications</p>
                <p className="text-gray-600 text-sm">Receive updates about your crops</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
              </label>
            </div>

            <div className="flex justify-between items-center p-4 border border-gray-200 rounded-lg">
              <div>
                <p className="font-semibold text-gray-900">Weather Alerts</p>
                <p className="text-gray-600 text-sm">Get notified about weather changes</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
              </label>
            </div>

            <button
              onClick={() => toast.info('Change password feature coming soon!')}
              className="w-full text-left p-4 border border-gray-200 rounded-lg hover:border-emerald-300 hover:bg-emerald-50 transition"
            >
              <p className="font-semibold text-gray-900">Change Password</p>
              <p className="text-gray-600 text-sm">Update your password regularly for security</p>
            </button>
          </div>
        </div>

        {/* Danger Zone */}
        {/* <div className="bg-red-50 border border-red-200 rounded-lg p-8">
          <h2 className="text-xl font-bold text-red-900 mb-4">⚠️ Danger Zone</h2>

          <div className="space-y-3">
            <button
              onClick={handleLogout}
              className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-3 px-4 rounded-lg transition"
            >
              Logout
            </button>

            <button
              onClick={() =>
                toast.warning('Account deletion is not yet available. Please contact support.')
              }
              className="w-full bg-red-100 hover:bg-red-200 text-red-900 font-semibold py-3 px-4 rounded-lg transition"
            >
              Delete Account
            </button>
          </div>
        </div> */}
      </div>
    </div>
  );
};
