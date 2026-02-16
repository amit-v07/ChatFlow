import React, { useEffect } from 'react';
import { useFriendStore } from '../../store/friendStore';
import { useAuthStore } from '../../store/authStore';

export const FriendRequests: React.FC = () => {
    const { pendingRequests, fetchPendingRequests, respondToRequest } = useFriendStore();
    const token = useAuthStore((state) => state.token);

    useEffect(() => {
        if (token) {
            fetchPendingRequests(token);
        }
    }, [token, fetchPendingRequests]);

    const handleRespond = (requestId: string, status: 'accepted' | 'rejected') => {
        if (token) {
            respondToRequest(requestId, status, token);
        }
    };

    if (pendingRequests.length === 0) {
        return null;
    }

    return (
        <div className="p-4 bg-white rounded-lg shadow mb-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-700">Friend Requests</h3>
            <div className="space-y-3">
                {pendingRequests.map((request) => (
                    <div key={request.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                        <div>
                            <p className="font-medium text-gray-900">{request.sender.email}</p>
                            <p className="text-xs text-gray-500">{new Date(request.created_at).toLocaleDateString()}</p>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => handleRespond(request.id, 'accepted')}
                                className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                            >
                                Accept
                            </button>
                            <button
                                onClick={() => handleRespond(request.id, 'rejected')}
                                className="px-3 py-1 text-sm bg-red-100 text-red-600 rounded hover:bg-red-200"
                            >
                                Reject
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
