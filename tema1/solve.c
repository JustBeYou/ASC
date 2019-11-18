#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_N 1000
#define MAX_S 1000

typedef enum {
    prime = 0,
    not_prime = 1
} primality;

primality sieve[MAX_N];
void compute_sieve(int p) {
    sieve[0] = sieve[1] = not_prime;

    for (int i = 2; i <= p; i++) {
        if (sieve[i] == prime) {
            for (int j = i * 2; j <= p; j += i) {
                sieve[j] = not_prime;
            }
        }
    }
}

int primes_cnt = 0;
int primes[MAX_N];
void compute_primes(int p) {
    for (int i = 2; i <= p; i++) {
        if (sieve[i] == prime) {
            primes[primes_cnt++] = i;
        }
    }
}

int find_generator(int p) {
    if (p == 2) return 1;

    // g este un numar prim mai mic decat p
    for (int i = 0; i < primes_cnt - 1; i++) {
        int g = primes[i];
        int g_pow = g;

        // calculam g ^ 2, g ^ 3, .., g ^ (p - 2) mod p
        // daca niciunul din rezultate nu este congruent cu 1
        // atunci ordinul lui g este p - 1, deci g este generator
        for (int j = 0; j < p - 3; j++) {
            g_pow *= g;
            g_pow %= p;

            if (g_pow == 1) {
                g = -1;
                break;
            }
        }

        if (g != -1) {
            return g;
        }
    }

    return -1;
}

// p >= 0
int pow_mod(int b, int e, int n) {
    if (e == 0) return 1;
    if (e == 1) return b % n;

    int res = b % n;
    for (int i = 0; i < e - 1; i++) {
        res *= b;
        res %= n;
    }

    return res;
}

// alfabet A..Z
void encrypt(char input[MAX_S], char output[MAX_S], int p, int g) {
    int i;
    for (i = 0; input[i] != '\0'; i++) {
        int temp = input[i] - 'A';
        temp = pow_mod(g, temp, p);
        output[i] = temp + 'A';
    }
    output[i] = '\0';
}

int log_mod(int b, int a, int n) { 
    int res = 1;
    for (int i = 0; i < n - 1; i++) {
        if (res == a) {
            return i;
        }

        res *= b;
        res %= n;
    }

    return -1;
}

void decrypt(char input[MAX_S], char output[MAX_S], int p, int g) {
    int i;
    for (i = 0; input[i] != '\0'; i++) {
        int temp = input[i] - 'A';
        temp = log_mod(g, temp, p);   
        output[i] = temp + 'A';
    }
    output[i] = '\0';
}
int main() {
    int p; 
    printf("p = ");
    scanf("%d", &p);

    // Precomputare ciur in O(p * log log p)
    compute_sieve(p);

    // Precomputare numere prime in O(p)
    compute_primes(p);

    // Daca p nu e prim => iesire
    if (sieve[p] == not_prime) {
        printf("p nu este prim\n");
        return 0;
    }

    // Cautam generatorul grupului (Zp*, *)
    // Numarul de numere prime pana la p este ~ p / ln(p)
    // Complexitate cautare O(p / ln(p) * (p - 2)) = O(p ^ 2 / ln(p))
    int g = find_generator(p);
    printf("g = %d\n", g);
    if (g == -1) return 0;

    char s[MAX_S];
    printf("s = ");
    fgets(s, MAX_S, stdin);
    fgets(s, MAX_S, stdin);
    for (int i = 0; s[i] != '\0'; i++) {
        if (s[i] == '\n') {
            s[i] = '\0';
        }
    }

    encrypt(s, s, p, g);
    printf("enc(s) = %s\n", s);

    decrypt(s, s, p, g);
    printf("dec(s) = %s\n", s);

    return 0;
}
