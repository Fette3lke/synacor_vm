#include <stdio.h>
#include <stdlib.h>

#define MAX_STACK 65000

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

void rec()                     // 6027
{
  printf("i: %5d, %5d, %5d, [%5d]\n", k++, reg[0], reg[1], loc);
  if (reg[0] != 0)                  // 6027
    if (reg[1] != 0)                // 6035
      {
        mypush(reg[0]);               // 6048
        reg[1] = (reg[1] + 32767) % 32768; // 6050
        rec();                      // 6054
        reg[1] = reg[0];            // 6056
        reg[0] = mypop();             // 6059
        reg[0] = (reg[0] + 32767) % 32768; // 6061
        rec();                      // 6065 -> 6067 ret
      }
    else                            // 6038
      {
        printf("reg1 == 0\n");
        z1++;
        reg[0] = (reg[0] + 32767) % 32768; // 6038
        //printf("reg0 ## loc: %d | %d\n", loc, reg[0]);
        reg[1] = reg[7];            // 6042
        rec();                      // 6045
      }
  else
    {
      z0++;
      reg[0] = (reg[1] + 1) % 32768;    // 6030  -> 6034 ret
      //printf("!!! %d\n", loc);
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
    }

  rec();

  for (i = 0; i<7; i++)
    printf("reg[%d]: %d\n", i, reg[i]);
  printf("z0: %d, z1: %d\n", z0, z1);



}
