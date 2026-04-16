import { useRef, useState, useCallback } from 'react';
// import { useWebSocket } from './useWebSocket'; // Or pass sendMessage from parent

const ICE_SERVERS = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        // Add TURN servers here for production
    ],
};

export const useWebRTC = (sendMessage: (msg: any) => void) => {
    const peerConnection = useRef<RTCPeerConnection | null>(null);
    const [localStream, setLocalStream] = useState<MediaStream | null>(null);
    const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);

    const createPeerConnection = useCallback(() => {
        if (peerConnection.current) return peerConnection.current;

        const pc = new RTCPeerConnection(ICE_SERVERS);

        pc.onicecandidate = (event) => {
            if (event.candidate) {
                sendMessage({
                    type: 'ice_candidate',
                    candidate: event.candidate,
                });
            }
        };

        pc.ontrack = (event) => {
            setRemoteStream(event.streams[0]);
        };

        if (localStream) {
            localStream.getTracks().forEach((track) => {
                pc.addTrack(track, localStream as MediaStream);
            });
        }

        peerConnection.current = pc;
        return pc;
    }, [sendMessage, localStream]);

    const startCall = useCallback(async (isVideo: boolean) => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: isVideo,
                audio: true,
            });
            setLocalStream(stream);

            // Update tracks if PC exists (unlikely at start but for safety)
            // Actually, we usually create PC when needed.

            return stream;
        } catch (error) {
            console.error('Error accessing media devices:', error);
            throw error;
        }
    }, []);

    const handleOffer = useCallback(async (offer: RTCSessionDescriptionInit) => {
        const pc = createPeerConnection();
        await pc.setRemoteDescription(new RTCSessionDescription(offer));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        sendMessage({
            type: 'answer',
            signal_data: answer,
        });
    }, [createPeerConnection, sendMessage]);

    const handleAnswer = useCallback(async (answer: RTCSessionDescriptionInit) => {
        if (peerConnection.current) {
            await peerConnection.current.setRemoteDescription(new RTCSessionDescription(answer));
        }
    }, []);

    const handleCandidate = useCallback(async (candidate: RTCIceCandidateInit) => {
        if (peerConnection.current) {
            await peerConnection.current.addIceCandidate(new RTCIceCandidate(candidate));
        }
    }, []);

    const endCall = useCallback(() => {
        if (peerConnection.current) {
            peerConnection.current.close();
            peerConnection.current = null;
        }
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            setLocalStream(null);
        }
        setRemoteStream(null);
    }, [localStream]);

    return {
        localStream,
        remoteStream,
        startCall,
        handleOffer,
        handleAnswer,
        handleCandidate,
        endCall,
        createPeerConnection,
        peerConnection
    };
};
