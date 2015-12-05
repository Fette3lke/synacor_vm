#include <stdio.h>
#include <stdlib.h>
//#include <math.h>

#define MAX_STACK 6

int reg[8];
int loc_5485 = 2;
int i, j, k = 0;
int stack[MAX_STACK];
int loc = 0;

int z0 = 0;
int z1 = 0;

void mypush(int i)
  {
    //printf("push %d <- %d | %d %d\n", loc, i, reg[0], reg[1]);
    if (loc == MAX_STACK)
      {
        printf("stack overflow: ");
        for (j = 0; j<10; j++)
          printf("%5d, ", stack[j]);
        printf("!\n");
        fflush(stdout);
        exit(0);
      }
    stack[loc] = i;
    loc += 1;
  }

int mypop()
  {
    //printf("pop %d\n", stack[loc]);
    return stack[--loc];
  }

int rec(int a, int b)                     // 6027
{
  //printf("%d %d\n", a, b);
  if (a == 1)
    return (b + reg[7] + 1) % 32768;
  if (a == 2)
    return ((2 * reg[7] + 1) + b * (reg[7] + 1)) % 32768;
  //if (a<3)
  //  return (int)((a-1) * (a * reg[7] + 1) + pow(b, a-1) * (reg[7] + 1)) % 32768;

  if (a != 0)                  // 6027
    if (b != 0)                // 6035
      {
        return rec(a-1, rec(a, b-1));                      // 6065 -> 6067 ret
      }
    else                            // 6038
      {
        return rec( (a-1), reg[7]);                      // 6045
      }
  else
    {
      return (b + 1) % 32768;    // 6030  -> 6034 ret
    }
}


int main (int argc, char *argv[])
{
  reg[7] = 111;
  reg[0] = loc_5485;
  reg[1] = 1;

  if (argc == 3)
    {
      reg[0] = atoi(argv[1]);
      reg[7] = atoi(argv[2]);
      printf("reg0: %d\n", rec(reg[0], reg[1]));
      return 0;
    }

  if (argc == 4)
    {
      reg[0] = atoi(argv[1]);
      reg[1] = atoi(argv[2]);
      reg[7] = atoi(argv[3]);
      printf("reg0: %d\n", rec(reg[0], reg[1]));
      return 0;
    }
  int l;
  for (l = 0; l < 32768; l++)
    {
      reg[7] = l;
      reg[0] = rec( 4, 1);
      printf("l: %d, %d\n", l, reg[0]);
      if (reg[0] == 6)
        break;
    }


}
