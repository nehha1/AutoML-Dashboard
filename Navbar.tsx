// components/Navbar.jsx

'use client';

import React from 'react';
import { useAuth } from '@clerk/nextjs'; // Ensure you're using Clerk's hooks
import Link from 'next/link'; // Adjust this import based on your routing library
import { Button } from "@/components/ui/button"; // Adjust based on your button component

const Navbar = () => {
  const { isSignedIn } = useAuth(); // Get the signed-in state from Clerk

  const links = [
    { name: 'Dashboard', path: '/' },
    { name: 'Models', path: '/models' },
    { name: 'Deployments', path: '/deployments' },
    { name: 'Settings', path: '/settings' },
    { name: 'Monitoring', path: '/monitoring' },
  ];

  return (
    <nav className="flex justify-between items-center p-4 bg-gray-800 text-white">
      <h1 className="text-xl font-bold">MLOps Hub</h1>
      <div className="flex space-x-4">
        {links.map((link) => (
          <Button
            key={link.name}
            variant="link"
            disabled={!isSignedIn} // Disable if not signed in
            className={`text-white ${!isSignedIn ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <Link href={link.path} className={`block ${!isSignedIn ? 'pointer-events-none' : ''}`}>
              {link.name}
            </Link>
          </Button>
        ))}
      </div>
    </nav>
  );
};

export default Navbar;
