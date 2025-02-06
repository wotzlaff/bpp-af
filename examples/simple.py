import bpp_af

def main():
    inst = bpp_af.Instance([1, 2, 3], 3)
    sol = bpp_af.solve(inst)
    val = len(sol)
    print('value:', val)
    print('solution:', sol)


if __name__ == '__main__':
    main()