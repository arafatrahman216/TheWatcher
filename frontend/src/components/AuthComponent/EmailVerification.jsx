// components/OtpVerifier.jsx
import React, { useState } from "react";
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  InputAdornment,
  IconButton,
  Chip
} from "@mui/material";
import { 
  VerifiedUser, 
  ArrowBack,
  Email as EmailIcon
} from "@mui/icons-material";

export default function OtpVerifier({ onVerify, onBack, email, loading }) {
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = () => {
    if (!otp.trim()) {
      setError("Please enter the verification code");
      return;
    }
    
    if (otp.length !== 6) {
      setError("Verification code must be 6 digits");
      return;
    }
    
    if (!/^\d+$/.test(otp)) {
      setError("Verification code must contain only numbers");
      return;
    }
    
    setError("");
    onVerify(otp);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const handleOtpChange = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
    setOtp(value);
    if (error) setError("");
  };

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      {/* Header with back button */}
      <Box display="flex" alignItems="center" gap={2}>
        <IconButton 
          onClick={onBack}
          disabled={loading}
          sx={{
            color: '#00ff7f',
            '&:hover': {
              color: '#00cc64',
              backgroundColor: 'rgba(0, 255, 127, 0.08)',
            },
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            borderRadius: 1,
          }}        >
          <ArrowBack />
        </IconButton>
        <Typography variant="h5" fontWeight="600" sx={{ color: '#ffffff' }}>
          Verify Email
        </Typography>
      </Box>

      {/* Description */}
      <Box textAlign="center" mb={2}>
        <Box display="flex" justifyContent="center" mb={2}>
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              background: 'linear-gradient(45deg, #667eea, #764ba2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2
            }}
          >
            <EmailIcon sx={{ color: 'white', fontSize: 32 }} />
          </Box>
        </Box>
        
        <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)' }} mb={2}>
          We've sent a 6-digit verification code to
        </Typography>
        
        <Chip
          label={email}
          variant="outlined"
          sx={{
            borderColor: '#667eea',
            color: '#667eea',
            fontWeight: 600,
            mb: 2
          }}
        />
        
        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
          Please enter the code below to verify your email address
        </Typography>
      </Box>

      {/* OTP Input */}
      <TextField
        label="Verification Code"
        fullWidth
        value={otp}
        onChange={handleOtpChange}
        onKeyPress={handleKeyPress}
        error={!!error}
        helperText={error || "Enter the 6-digit code from your email"}
        disabled={loading}
        placeholder="000000"
        inputProps={{
          maxLength: 6,
          style: { 
            textAlign: 'center', 
            fontSize: '1.5rem', 
            letterSpacing: '0.5rem',
            fontWeight: 600
          }
        }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <VerifiedUser color="action" />
            </InputAdornment>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 2,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            '& fieldset': {
              borderColor: 'rgba(0, 255, 127, 0.3)',
            },
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              '& fieldset': {
                borderColor: 'rgba(0, 255, 127, 0.5)',
              },
            },
            '&.Mui-focused': {
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              '& fieldset': {
                borderColor: '#00ff7f',
                borderWidth: '2px',
              },
            },
          },
          '& .MuiInputLabel-root': {
            color: 'rgba(255, 255, 255, 0.7)',
            '&.Mui-focused': {
              color: '#00ff7f',
            },
          },
          '& .MuiOutlinedInput-input': {
            color: '#ffffff',
          },
          '& .MuiInputAdornment-root .MuiSvgIcon-root': {
            color: 'rgba(255, 255, 255, 0.5)',
          },
          '& .MuiFormHelperText-root': {
            color: 'rgba(255, 255, 255, 0.6)',
          },
        }}
      />

      {/* Verify Button */}
      <Button
        variant="contained"
        fullWidth
        onClick={handleSubmit}
        disabled={loading || !otp}
        sx={{
          py: 1.5,
          mt: 2,
          borderRadius: 2,
          background: 'linear-gradient(45deg, #00ff7f, #00cc64)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: '-100%',
            width: '100%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
            transition: 'left 0.5s',
          },
          '&:hover': {
            background: 'linear-gradient(45deg, #00cc64, #00a050)',
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(0, 255, 127, 0.4)',
            '&::before': {
              left: '100%',
            },
          },
          '&:active': {
            transform: 'translateY(-1px)',
          },
          '&:disabled': {
            background: '#333333',
            color: '#666666',
            transform: 'none',
            boxShadow: 'none',
          },
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          textTransform: 'none',
          fontSize: '1rem',
          fontWeight: 600,
          color: '#000000',
        }}
      >
        {loading ? "Verifying..." : "Verify Email"}
      </Button>

      {/* Resend option */}
      <Box textAlign="center" mt={2}>
        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
          Didn't receive the code?{' '}
          <Button 
            variant="text" 
            size="small" 
            disabled={loading}
            sx={{ 
              textTransform: 'none', 
              color: '#00ff7f',
              '&:hover': { backgroundColor: 'rgba(0, 255, 127, 0.1)' }
            }}
          >
            Resend Code
          </Button>
        </Typography>
      </Box>
    </Box>
  );
}
