#pragma once
// WeirdExt offsets — macOS ARM64
//
// Roblox Version  : 0.745.0.7451137
// Binary SHA-256  : 8af3f95d347a5283618dd9c17f4a1b02b59982ff699f00cc6f2a195377f2f6b7
// Dumped At       : 2026-11-14 20:54 UTC
// Total Offsets   : 29
//
// macOS layouts differ from Windows; use these with the macOS client only.

#include <cstdint>

namespace Offsets {
    namespace Instance {
        inline constexpr uintptr_t Name = 0x68;  // pointer to std::string
        inline constexpr uintptr_t Parent = 0x60;
        inline constexpr uintptr_t ChildrenStart = 0x70;  // pointer to a vector of 16-byte smart pointers
        inline constexpr uintptr_t ChildrenEnd = 0x8;  // end pointer, relative to the children vector
        inline constexpr uintptr_t This = 0x8;  // (self, control block) smart pointer pair
    }
    namespace Players {
        inline constexpr uintptr_t LocalPlayer = 0x108;
    }
    namespace Player {
        inline constexpr uintptr_t ModelInstance = 0x258;
        inline constexpr uintptr_t Team = 0x298;
    }
    namespace Workspace {
        inline constexpr uintptr_t CurrentCamera = 0x458;
    }
    namespace Camera {
        inline constexpr uintptr_t Rotation = 0xb8;  // nine floats, row-major; Position follows at +36
        inline constexpr uintptr_t Position = 0xdc;
        inline constexpr uintptr_t FieldOfView = 0x120;  // float, radians (vertical)
        inline constexpr uintptr_t CameraSubject = 0xa8;  // (object, control block) smart pointer pair
    }
    namespace BasePart {
        inline constexpr uintptr_t Primitive = 0x168;
    }
    namespace Primitive {
        inline constexpr uintptr_t Rotation = 0xb0;  // nine floats, row-major; Position follows at +36
        inline constexpr uintptr_t Position = 0xd4;
        inline constexpr uintptr_t Flags = 0x1be;
        inline constexpr uintptr_t AssemblyLinearVelocity = 0xe0;  // copy refreshed from the solver body each physics step
    }
    namespace Humanoid {
        inline constexpr uintptr_t Health = 0x174;
        inline constexpr uintptr_t MaxHealth = 0x18c;
        inline constexpr uintptr_t WalkSpeed = 0x1b4;
        inline constexpr uintptr_t WalkSpeedCheck = 0x38c;  // must equal WalkSpeed
        inline constexpr uintptr_t JumpPower = 0x188;
        inline constexpr uintptr_t UseJumpPower = 0x1c6;  // bool
    }
    namespace PrimitiveFlags {
        inline constexpr uintptr_t CanCollide = 0x8;  // bit mask in Primitive::Flags (a byte)
    }
    namespace SolverBody {
        inline constexpr uintptr_t Pointer = 0x140;  // Primitive -> solver body that physics integrates
        inline constexpr uintptr_t Position = 0x98;  // Vector3; copies follow every BlockStride bytes
        inline constexpr uintptr_t Velocity = 0xa4;  // Vector3; write here to change motion mid-air
        inline constexpr uintptr_t BlockStride = 0x48;  // bytes between (position, velocity) copies
    }
}
