import asyncio
import aiohttp

from binairo import Binairo

base_url = "https://binarypuzzle.com/puzzles.php"
url = base_url + "?size=%d&level=%d&nr=%d"


async def solve(url: str, session: aiohttp.ClientSession):
    async with session.get(url) as response:
        html = await response.text("iso-8859-1")
        puzzle, solution = Binairo.from_html(html)
        puzzle.solve()
        return puzzle, solution
    
async def check_puzzle(size: int, level: int, nr: int):
    for i in range(nr, nr + 20):
        async with aiohttp.ClientSession() as session:
            print(f"making puzzle {nr + i} of size {size} at level {level}")
            puzzle, solution = await solve(url % (size, level, nr + i), session)
            if puzzle == solution:
                print(f"Successfully solved puzzle {nr + i} of size {size} at level {level}")
            else:
                print(f"Failed to solve puzzle {nr + i} of size {size} at level {level}")

async def main():
    for level in range(4):
        await asyncio.gather(*[check_puzzle(6, level, i) for i in range(1, 200, 20)])
    
if __name__ == "__main__":
    asyncio.run(main())