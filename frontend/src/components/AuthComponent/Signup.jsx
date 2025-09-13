// components/SignupForm.jsx
import React, { useState } from "react";
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  InputAdornment, 
  IconButton 
} from "@mui/material";
import { 
  Person, 
  Email, 
  Lock, 
  Visibility, 
  VisibilityOff 
} from "@mui/icons-material";

export default function SignupForm({ onSignup, loading }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    
    if (!name.trim()) {
      newErrors.name = "Name is required";
    } else if (name.trim().length < 2) {
      newErrors.name = "Name must be at least 2 characters";
    }
    
    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = "Please enter a valid email";
    }
    
    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onSignup(name, email, password);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <Box display="flex" flexDirection="column" gap={3}>
      <Box textAlign="center" mb={2}>
        <Typography variant="h5" fontWeight="600" sx={{ color: '#ffffff' }}>
          Create Account
        </Typography>
        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)' }} mt={1}>
          Join The Watcher to start monitoring your websites
        </Typography>
      </Box>

      <TextField
        label="Full Name"
        fullWidth
        value={name}
        onChange={(e) => {
          setName(e.target.value);
          if (errors.name) setErrors({ ...errors, name: null });
        }}
        onKeyPress={handleKeyPress}
        error={!!errors.name}
        helperText={errors.name}
        disabled={loading}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Person color="action" />
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
        }}
      />

      <TextField
        label="Email Address"
        type="email"
        fullWidth
        value={email}
        onChange={(e) => {
          setEmail(e.target.value);
          if (errors.email) setErrors({ ...errors, email: null });
        }}
        onKeyPress={handleKeyPress}
        error={!!errors.email}
        helperText={errors.email}
        disabled={loading}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Email color="action" />
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
        }}
      />

      <TextField
        label="Password"
        type={showPassword ? 'text' : 'password'}
        fullWidth
        value={password}
        onChange={(e) => {
          setPassword(e.target.value);
          if (errors.password) setErrors({ ...errors, password: null });
        }}
        onKeyPress={handleKeyPress}
        error={!!errors.password}
        helperText={errors.password || "Minimum 6 characters required"}
        disabled={loading}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Lock color="action" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={() => setShowPassword(!showPassword)}
                edge="end"
                disabled={loading}
              >
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
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
          '& .MuiIconButton-root': {
            color: 'rgba(255, 255, 255, 0.5)',
            '&:hover': {
              color: '#00ff7f',
            },
          },
        }}
      />

      <Button
        variant="contained"
        fullWidth
        onClick={handleSubmit}
        disabled={loading}
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
        {loading ? "Creating Account..." : "Create Account"}
      </Button>
    </Box>
  );
}
