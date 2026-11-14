/*
 * sweepc.c — native heap sweeper for the Roblox offset dumper.
 *
 * Runs as root (invoked from the sudo'd python dumper), attaches to the
 * Roblox task, and does the two hot sweeps natively:
 *
 *   sweepc spans <pid> <lo:hi>...     -> records (addr, value) for every
 *                                        8-byte-aligned qword in writable
 *                                        anonymous memory whose value falls
 *                                        in any given [lo,hi) span.
 *   sweepc find  <pid> <limit-per>    -> reads NUL-free needle lines from
 *                                        stdin, emits (addr, needle-index)
 *                                        for every literal occurrence.
 *
 * Output is a binary stream on stdout, records as little-endian
 * (u64, u64) for spans and (u64, u32) for find. Progress goes to stderr.
 *
 * Build: clang -O2 -o sweepc sweepc.c
 */

#include <libproc.h>
#include <mach/mach.h>
#include <mach/mach_vm.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define CHUNK_SIZE (4u << 20)
#define PROGRESS_EVERY (512u << 20)

typedef struct {
    unsigned long long lo;
    unsigned long long hi;
} Span;

static void emit_spans(const unsigned char *buf, unsigned long long base,
                       unsigned long long len, const Span *spans, int span_count,
                       FILE *out);
static void emit_find(const unsigned char *buf, unsigned long long base,
                      unsigned long long len, char **needles, size_t *needle_len,
                      int needle_count, unsigned limit_per, FILE *out,
                      unsigned *emitted_per);

static void scan_range(mach_port_t task, unsigned long long addr,
                       unsigned long long size, unsigned char *buffer,
                       const char *mode, const Span *spans, int span_count,
                       char **needles, size_t *needle_len, int needle_count,
                       unsigned limit_per, FILE *out, unsigned *emitted_per,
                       unsigned long long *scanned);

static void process_buffer(const unsigned char *buf, unsigned long long base,
                           unsigned long long len, const char *mode,
                           const Span *spans, int span_count, char **needles,
                           size_t *needle_len, int needle_count,
                           unsigned limit_per, FILE *out, unsigned *emitted_per,
                           unsigned long long *scanned) {
    *scanned += len;
    if (*scanned / PROGRESS_EVERY != (*scanned - len) / PROGRESS_EVERY) {
        fprintf(stderr, "  · sweepc %.2f GiB\n", *scanned / 1073741824.0);
        fflush(stderr);
    }
    if (strcmp(mode, "spans") == 0) {
        emit_spans(buf, base, len, spans, span_count, out);
    } else {
        emit_find(buf, base, len, needles, needle_len, needle_count,
                  limit_per, out, emitted_per);
    }
}

/* Read [addr, addr+size) skipping holes: on a failed read the range is
 * bisected down to 64 KiB, mirroring the python sweep's hole handling. A
 * region with uncommitted pages must not lose whole 4 MiB chunks. */
static void scan_range(mach_port_t task, unsigned long long addr,
                       unsigned long long size, unsigned char *buffer,
                       const char *mode, const Span *spans, int span_count,
                       char **needles, size_t *needle_len, int needle_count,
                       unsigned limit_per, FILE *out, unsigned *emitted_per,
                       unsigned long long *scanned) {
    const unsigned long long LEAF = 1u << 16;
    if (size == 0) return;
    mach_vm_size_t got = 0;
    kern_return_t kr = mach_vm_read_overwrite(task, addr, size,
                                              (vm_address_t)buffer, &got);
    if (kr == KERN_SUCCESS && got > 0) {
        process_buffer(buffer, addr, got, mode, spans, span_count, needles,
                       needle_len, needle_count, limit_per, out, emitted_per,
                       scanned);
        return;
    }
    if (size <= LEAF) return;              /* hole: skip */
    unsigned long long mid = (size / 2) & ~0xfffULL;
    scan_range(task, addr, mid, buffer, mode, spans, span_count, needles,
               needle_len, needle_count, limit_per, out, emitted_per, scanned);
    scan_range(task, addr + mid, size - mid, buffer + mid, mode, spans,
               span_count, needles, needle_len, needle_count, limit_per, out,
               emitted_per, scanned);
}

static void emit_spans(const unsigned char *buf, unsigned long long base,
                       unsigned long long len, const Span *spans, int span_count,
                       FILE *out) {
    unsigned long long aligned = (base + 7) & ~7ULL;
    unsigned long long offset = aligned - base;
    for (; offset + 8 <= len; offset += 8) {
        unsigned long long value;
        memcpy(&value, buf + offset, 8);
        for (int i = 0; i < span_count; i++) {
            if (value >= spans[i].lo && value < spans[i].hi) {
                unsigned long long record[2] = {base + offset, value};
                fwrite(record, 8, 2, out);
                break;
            }
        }
    }
}

static void emit_find(const unsigned char *buf, unsigned long long base,
                      unsigned long long len, char **needles, size_t *needle_len,
                      int needle_count, unsigned limit_per, FILE *out,
                      unsigned *emitted_per) {
    for (int i = 0; i < needle_count; i++) {
        if (emitted_per[i] >= limit_per) continue;
        const unsigned char *cursor = buf;
        unsigned long long remaining = len;
        while (remaining >= needle_len[i]) {
            const unsigned char *hit = memmem(cursor, remaining,
                                              needles[i], needle_len[i]);
            if (!hit) break;
            unsigned long long addr = base + (unsigned long long)(hit - buf);
            unsigned long long record[2] = {addr, (unsigned long long)i};
            fwrite(record, 8, 2, out);
            emitted_per[i]++;
            if (emitted_per[i] >= limit_per) break;
            remaining = len - (unsigned long long)(hit - buf) - needle_len[i];
            cursor = hit + needle_len[i];
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: %s spans <pid> <lo:hi>... | %s find <pid> <limit-per> < needles\n",
                argv[0], argv[0]);
        return 2;
    }
    const char *mode = argv[1];
    int pid = strcmp(argv[2], "self") == 0 ? getpid() : atoi(argv[2]);

    mach_port_t self_task = mach_task_self();
    mach_port_t task = MACH_PORT_NULL;
    kern_return_t kr;
    if (pid == getpid()) {
        task = self_task;   /* self-attach needs no privileges */
    } else {
        kr = task_for_pid(self_task, pid, &task);
        if (kr != KERN_SUCCESS) {
            fprintf(stderr, "task_for_pid(%d) failed: %d (run as root)\n", pid, kr);
            return 3;
        }
    }

    Span spans[64];
    int span_count = 0;
    unsigned limit_per = 64;
    if (strcmp(mode, "spans") == 0) {
        for (int i = 3; i < argc && span_count < 64; i++) {
            if (sscanf(argv[i], "%llx:%llx", &spans[span_count].lo,
                       &spans[span_count].hi) == 2) {
                span_count++;
            }
        }
        if (span_count == 0) {
            fprintf(stderr, "no valid lo:hi spans\n");
            return 2;
        }
    } else if (strcmp(mode, "find") == 0 && argc >= 4) {
        limit_per = (unsigned)strtoul(argv[3], NULL, 10);
    } else {
        fprintf(stderr, "unknown mode %s\n", mode);
        return 2;
    }

    /* needle mode: one needle per stdin line */
    char *needles[64];
    size_t needle_len[64];
    unsigned emitted_per[64] = {0};
    int needle_count = 0;
    if (strcmp(mode, "find") == 0) {
        char line[256];
        while (needle_count < 64 && fgets(line, sizeof(line), stdin)) {
            size_t n = strlen(line);
            while (n && (line[n - 1] == '\n' || line[n - 1] == '\r')) n--;
            if (n == 0) continue;
            needles[needle_count] = malloc(n);
            memcpy(needles[needle_count], line, n);
            needle_len[needle_count] = n;
            needle_count++;
        }
        if (needle_count == 0) {
            fprintf(stderr, "no needles on stdin\n");
            return 2;
        }
    }

    unsigned char *buffer = malloc(CHUNK_SIZE);
    if (!buffer) return 4;

    /* walk the VM map exactly like the python side: basic info 64 */
    mach_vm_address_t address = 1;
    unsigned long long scanned = 0;
    FILE *out = stdout;
    for (;;) {
        mach_vm_size_t size = 0;
        mach_vm_address_t probe = address;
        struct vm_region_basic_info_64 info;
        mach_msg_type_number_t count = VM_REGION_BASIC_INFO_COUNT_64;
        mach_port_t object_name = MACH_PORT_NULL;
        kr = mach_vm_region(task, &probe, &size, VM_REGION_BASIC_INFO_64,
                            (vm_region_info_t)&info, &count, &object_name);
        if (kr != KERN_SUCCESS || size == 0) break;

        int anonymous = 1;
        char path[4096] = {0};
        if (proc_regionfilename(pid, probe, path, sizeof(path)) > 0) {
            anonymous = 0;
        }
        int readable = (info.protection & VM_PROT_READ) != 0;
        if (readable && anonymous) {
            for (unsigned long long chunk = probe;
                 chunk < probe + size; chunk += CHUNK_SIZE) {
                unsigned long long want = (probe + size) - chunk;
                if (want > CHUNK_SIZE) want = CHUNK_SIZE;
                scan_range(task, chunk, want, buffer, mode, spans, span_count,
                           needles, needle_len, needle_count, limit_per, out,
                           emitted_per, &scanned);
            }
        }

        mach_vm_address_t next = probe + size;
        if (next <= probe) break;
        address = next;
    }

    fflush(out);
    free(buffer);
    fprintf(stderr, "  · sweepc done: %.2f GiB scanned\n", scanned / 1073741824.0);
    return 0;
}
